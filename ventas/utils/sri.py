# utils/sri.py
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from lxml import etree
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding
from cryptography.hazmat.backends import default_backend

from zeep import Client, Settings
from django.conf import settings
from xades_bes_sri_ec import xades
import tempfile, os

# Cargar/convertir certificados
from cryptography.hazmat.primitives.serialization import pkcs12
from zeep import Client, Settings
from zeep.transports import Transport
import requests

from cryptography import x509
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from cryptography.x509.oid import NameOID, ObjectIdentifier

OID_SERIALNUMBER = ObjectIdentifier("2.5.4.5")  # serialNumber

def derivar_ruc_desde_cert(cert: x509.Certificate) -> dict:
    """
    Intenta derivar el RUC del emisor a partir del certificado.
    Retorna: {"ci": "...", "ruc": "...", "raw": {"serialNumber": "...", "cn": "..."}}
    - Si encuentra cédula (10 dígitos), propone RUC = ci + "001".
    - Si encuentra 13 dígitos válidos, los asume como RUC.
    """
    out = {"ci": None, "ruc": None, "raw": {}}
    nombre = cert.subject

    # serialNumber (2.5.4.5)
    try:
        serial_num = nombre.get_attributes_for_oid(OID_SERIALNUMBER)[0].value.strip()
        out["raw"]["serialNumber"] = serial_num
    except Exception:
        serial_num = None

    # CN por si aporta pista
    try:
        cn = nombre.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value.strip()
        out["raw"]["cn"] = cn
    except Exception:
        cn = None

import lxml.etree as ET

def extraer_ruc_xml(xml_bytes: bytes) -> str:
    root = ET.fromstring(xml_bytes)
    # Soporta namespaces o no: busque ‘ruc’ en cualquier parte bajo infoTributaria
    ns = root.nsmap.copy()
    if None in ns: ns.pop(None)
    ruc_nodes = root.xpath("//*[local-name()='infoTributaria']/*[local-name()='ruc']")
    if not ruc_nodes:
        raise ValueError("No se encontró <ruc> en <infoTributaria> del XML.")
    return (ruc_nodes[0].text or "").strip()


    # Heurística: primero mire 13 dígitos seguidos, luego 10 dígitos (CI)
    import re
    def solo_digitos(s): return re.sub(r"\D+", "", s or "")

    cand = solo_digitos(serial_num) or solo_digitos(cn)

    # Si hay 13 dígitos, asuma RUC directamente
    m13 = re.search(r"\b(\d{13})\b", cand)
    if m13:
        out["ruc"] = m13.group(1)
        return out

    # Si hay 10 dígitos, asuma cédula -> derive RUC natural (ci + "001")
    m10 = re.search(r"\b(\d{10})\b", cand)
    if m10:
        out["ci"] = m10.group(1)
        out["ruc"] = m10.group(1) + "001"
        return out

    # Plan B: escanear todo el DN por 13 primero y luego 10
    dn_text = ",".join([f"{r.oid.dotted_string}={r.value}" for r in nombre.rdns for r in r])
    dn_digits = solo_digitos(dn_text)
    m13 = re.search(r"\b(\d{13})\b", dn_digits)
    if m13:
        out["ruc"] = m13.group(1)
        return out
    m10 = re.search(r"\b(\d{10})\b", dn_digits)
    if m10:
        out["ci"] = m10.group(1)
        out["ruc"] = m10.group(1) + "001"

    return out


# Llamaremos directamente a la función estable del fork:

# ---------- A) Clave de acceso (49 dígitos) ----------
# Estructura: ddMMyyyy + codDoc + RUC + ambiente + serie(establecimiento+ptoEmi) + secuencial(9) + codigoNumerico(8) + tipoEmision + digitoVerificador
# Módulo 11 con ponderadores 2..7 (de derecha a izquierda). (Ficha técnica / comparativos SRI) 
# https://www.sri.gob.ec/... Versión 2.26+ (ver tabla y ejemplo de módulo 11)
# --- coloque esto cerca de sus imports ---
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from datetime import datetime, date
try:
    from zoneinfo import ZoneInfo
    TZ_EC = ZoneInfo("America/Guayaquil")
except Exception:
    TZ_EC = None

def _digits(val) -> str:
    """Solo dígitos."""
    return "".join(ch for ch in str(val) if ch.isdigit())

def _zfill_digits(val, width: int) -> str:
    """Extrae dígitos y left-pad a width."""
    return _digits(val).zfill(width)

def D(x, default="0.00") -> Decimal:
    """
    Convierte x a Decimal de forma tolerante:
    - Acepta None, "", números, y cadenas con coma decimal o símbolo '%'.
    - Elimina separadores no numéricos.
    """
    if x is None:
        return Decimal(default)
    if isinstance(x, (int, float, Decimal)):
        return Decimal(str(x))
    s = str(x).strip()
    if s == "":
        return Decimal(default)
    s = s.replace(" ", "").replace("%", "").replace(",", ".")
    s_filtrada = "".join(ch for ch in s if (ch.isdigit() or ch in ".-"))
    try:
        return Decimal(s_filtrada if s_filtrada else default)
    except InvalidOperation:
        return Decimal(default)


def _mod11(s: str) -> int:
    factores = [2,3,4,5,6,7]
    total = 0
    for i, ch in enumerate(reversed(s)):
        total += int(ch) * factores[i % len(factores)]
    dig = 11 - (total % 11)
    if dig == 11: return 0
    if dig == 10: return 1
    return dig

def generar_clave_acceso(fecha_emision, codDoc: str, ruc: str, ambiente: str,
                         estab: str, ptoemi: str, secuencial, codigo_numerico, tipo_emision: str) -> str:
    fdate = _parse_fecha_emision_ddmmyyyy(fecha_emision)
    fecha_ddmmyyyy = fdate.strftime("%d%m%Y")  # <<-- lo que exige la clave

    sec = str(int(secuencial)).zfill(9)
    serie = f"{estab}{ptoemi}"
    codigo_numerico = str(codigo_numerico).zfill(8)[-8:]  # fuerzo 8 dígitos

    base = f"{fecha_ddmmyyyy}{codDoc}{ruc}{ambiente}{serie}{sec}{codigo_numerico}{tipo_emision}"
    dv = _mod11(base)
    return f"{base}{dv}"

# utils/sri.py
from datetime import datetime, date

def _parse_fecha_emision_ddmmyyyy(fecha_emision) -> date:
    """
    Acepta str 'dd/mm/yyyy', datetime o date, y devuelve date.
    Si no puede, cae a hoy en Guayaquil.
    """
    if isinstance(fecha_emision, date) and not isinstance(fecha_emision, datetime):
        return fecha_emision
    if isinstance(fecha_emision, datetime):
        try:
            from zoneinfo import ZoneInfo
            return fecha_emision.astimezone(ZoneInfo("America/Guayaquil")).date()
        except Exception:
            return fecha_emision.date()
    if isinstance(fecha_emision, str):
        try:
            return datetime.strptime(fecha_emision, "%d/%m/%Y").date()
        except ValueError:
            pass
    # fallback
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("America/Guayaquil")).date()
    except Exception:
        from django.utils import timezone
        return timezone.localtime().date()


# ---------- B) Tipo de identificación del comprador ----------
def tipo_identificacion(ident: str) -> str:
    if not ident: return "07"  # consumidor final
    ident = ident.strip()
    if len(ident) == 13: return "04"  # RUC
    if len(ident) == 10: return "05"  # cédula
    return "06"                       # pasaporte/otros

# ---------- C) Código de porcentaje IVA según tarifa ----------
# Según actualizaciones de la Tabla 17 (versión 2.26), se manejan códigos como:
# 0 = 0%, 4 = 15%, 5 = 5%, 6 = No objeto, 7 = Exento, 2 = (históricamente general 12%), 3 = 14%.
# Ver "Ficha Técnica Esquema Offline v2.26/2.28" y resúmenes de cambios. 
def codigo_porcentaje_iva(tarifa: Decimal) -> str:
    t = tarifa.quantize(Decimal("0.01"))
    if t == Decimal("0"):   return "0"
    if t == Decimal("5"):   return "5"
    if t == Decimal("14"):  return "3"
    if t in (Decimal("12"), Decimal("13"), Decimal("15")):
        # Tarifa general (históricamente 12%, actualizada por normativa; SRI actualizó Tabla 17).
        # Para 15% la Tabla 17 vigente asigna código 4. 
        return "4" if t == Decimal("15") else "2"
    # fallback
    return "2"

def _to_fecha_str_dddmyyyy(f):
    # si ya viene str (dd/mm/yyyy), úsala tal cual
    if isinstance(f, str):
        return f
    # si viene date/datetime, formatea en zona de Ecuador
    if isinstance(f, datetime):
        return f.astimezone(ZoneInfo("America/Guayaquil")).strftime("%d/%m/%Y")
    if isinstance(f, date):
        return f.strftime("%d/%m/%Y")
    # fallback: ahora en Ecuador
    return datetime.now(ZoneInfo("America/Guayaquil")).strftime("%d/%m/%Y")

# ---------- D) Armado del XML de factura (versión 1.1.0) ----------
# Nota: Estructura base conforme a XSD factura v1.1.0 (válida en Offline). Ver anexos de la Ficha Técnica. 
def construir_factura_xml(context: dict, clave_acceso: str, secuencial: int) -> bytes:
    from lxml import etree
    from django.conf import settings
    from zoneinfo import ZoneInfo
    from datetime import datetime, date
    TZ_EC = ZoneInfo("America/Guayaquil")
    try:
        from zoneinfo import ZoneInfo
        TZ_EC = ZoneInfo("America/Guayaquil")
    except Exception:
        TZ_EC = None

    NSMAP = None
    root = etree.Element("factura", id="comprobante", version="1.1.0", nsmap=NSMAP)

    # infoTributaria
    it = etree.SubElement(root, "infoTributaria")
    etree.SubElement(it, "ambiente").text      = settings.SRI_AMBIENTE
    etree.SubElement(it, "tipoEmision").text   = settings.SRI_TIPO_EMISION
    etree.SubElement(it, "razonSocial").text   = settings.SRI_RAZON_SOCIAL
    etree.SubElement(it, "nombreComercial").text = settings.SRI_NOMBRE_COMERCIAL
    etree.SubElement(it, "ruc").text           = settings.SRI_RUC
    etree.SubElement(it, "claveAcceso").text   = clave_acceso
    etree.SubElement(it, "codDoc").text        = "01"
    etree.SubElement(it, "estab").text         = settings.SRI_ESTAB
    etree.SubElement(it, "ptoEmi").text        = settings.SRI_PTO_EMI
    sec9 = _zfill_digits(secuencial, 9)  # en vez de f"{secuencial:09d}"
    etree.SubElement(it, "secuencial").text = sec9
    etree.SubElement(it, "dirMatriz").text     = settings.SRI_DIR_MATRIZ

    # infoFactura
    inf = etree.SubElement(root, "infoFactura")
    fecha = _to_fecha_str_dddmyyyy(context.get("fecha"))
    etree.SubElement(inf, "fechaEmision").text = fecha
    etree.SubElement(inf, "dirEstablecimiento").text = settings.SRI_DIR_ESTABLECIMIENTO
    etree.SubElement(inf, "obligadoContabilidad").text = "SI"

    tipo_id = "07"
    ident = context.get("cedula")
    if ident:
        ident = str(ident).strip()
        if len(ident) == 13: tipo_id = "04"
        elif len(ident) == 10: tipo_id = "05"
        else: tipo_id = "06"
    etree.SubElement(inf, "tipoIdentificacionComprador").text = tipo_id
    comprador = f"{context.get('nombre','').strip()} {context.get('apellidos','').strip()}".strip() or "CONSUMIDOR FINAL"
    etree.SubElement(inf, "razonSocialComprador").text = comprador
    etree.SubElement(inf, "identificacionComprador").text = context.get("cedula") or "9999999999999"
    etree.SubElement(inf, "direccionComprador").text = context.get("direccion","")

    # --- Totales robustos ---
    subtotal      = D(context.get("subtotal"))
    descuento     = D(context.get("descuento"))
    subtotal_desc = D(context.get("subtotalD", subtotal - descuento))
    iva_total     = D(context.get("iva"))
    total         = D(context.get("total"))
    tarifa_iva    = D(context.get("porcentaje", "15"))

    etree.SubElement(inf, "totalSinImpuestos").text = str(subtotal_desc.quantize(Decimal("0.01")))
    etree.SubElement(inf, "totalDescuento").text    = str(descuento.quantize(Decimal("0.01")))

    # Código porcentaje IVA (ajuste simple)
    def codigo_porcentaje_iva(tarifa: Decimal) -> str:
        t = tarifa.quantize(Decimal("0.01"))
        if t == Decimal("0"):  return "0"
        if t == Decimal("5"):  return "5"
        if t == Decimal("14"): return "3"
        return "4" if t == Decimal("15") else "2"   # 15%->4; 12% histórico->2

    tci = etree.SubElement(inf, "totalConImpuestos")

    if tarifa_iva > 0:
        tip = etree.SubElement(tci, "totalImpuesto")
        etree.SubElement(tip, "codigo").text = "2"  # IVA
        etree.SubElement(tip, "codigoPorcentaje").text = codigo_porcentaje_iva(tarifa_iva)
        etree.SubElement(tip, "baseImponible").text = str(subtotal_desc.quantize(Decimal("0.01")))
        etree.SubElement(tip, "tarifa").text = str(tarifa_iva.quantize(Decimal("0.01")))
        valor_iva = (subtotal_desc * tarifa_iva / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        etree.SubElement(tip, "valor").text = str(valor_iva)
    else:
        # 0% (si aplica)
        tip = etree.SubElement(tci, "totalImpuesto")
        etree.SubElement(tip, "codigo").text = "2"
        etree.SubElement(tip, "codigoPorcentaje").text = "0"
        etree.SubElement(tip, "baseImponible").text = str(subtotal_desc.quantize(Decimal("0.01")))
        etree.SubElement(tip, "tarifa").text = "0.00"
        etree.SubElement(tip, "valor").text = "0.00"


    importe_total = (subtotal_desc + (valor_iva if tarifa_iva > 0 else D("0.00"))).quantize(Decimal("0.01"))
    etree.SubElement(inf, "propina").text = "0.00"
    etree.SubElement(inf, "importeTotal").text = str(importe_total)
    etree.SubElement(inf, "moneda").text = "DOLAR"


    # Pagos
    pagos = etree.SubElement(inf, "pagos")
    forma_map = {
        "Efectivo": "01", "Transferencia": "20", "Tarjeta crédito": "19", "Tarjeta débito": "16",
        "Cheque": "20", "Depósito": "20"
    }
    forma = forma_map.get(context.get("tipoPago","Efectivo"), "01")
    pago = etree.SubElement(pagos, "pago")
    etree.SubElement(pago, "formaPago").text = forma
    etree.SubElement(pago, "total").text = str(total.quantize(Decimal("0.01")))
    etree.SubElement(pago, "plazo").text = "0"
    etree.SubElement(pago, "unidadTiempo").text = "dias"

    # detalles
    detalles = etree.SubElement(root, "detalles")
    productos = context.get("productos", [])
    for item in productos:
        det = etree.SubElement(detalles, "detalle")
        etree.SubElement(det, "codigoPrincipal").text = str(item.get("codigo", item.get("id","")))
        desc = f"{item.get('modelo','')} {item.get('color','')}".strip()
        etree.SubElement(det, "descripcion").text = desc or "Item"
        etree.SubElement(det, "cantidad").text = str(D(item.get("cantidad")).quantize(Decimal("0.00")))
        precio_unit = D(item.get("precio"))
        etree.SubElement(det, "precioUnitario").text = str(precio_unit.quantize(Decimal("0.01")))
        etree.SubElement(det, "descuento").text = "0.00"
        precio_total_sin_imp = D(item.get("preciot"))
        etree.SubElement(det, "precioTotalSinImpuesto").text = str(precio_total_sin_imp.quantize(Decimal("0.01")))

        if tarifa_iva > 0:
            imps = etree.SubElement(det, "impuestos")
            imp = etree.SubElement(imps, "impuesto")
            etree.SubElement(imp, "codigo").text = "2"
            etree.SubElement(imp, "codigoPorcentaje").text = codigo_porcentaje_iva(tarifa_iva)
            etree.SubElement(imp, "tarifa").text = str(tarifa_iva.quantize(Decimal("0.01")))
            base_lin = precio_total_sin_imp
            etree.SubElement(imp, "baseImponible").text = str(base_lin.quantize(Decimal("0.01")))
            val_lin = (base_lin * tarifa_iva / Decimal("100")).quantize(Decimal("0.01"))
            etree.SubElement(imp, "valor").text = str(val_lin)

    # infoAdicional
    iad = etree.SubElement(root, "infoAdicional")
    for etiqueta, valor in [
        ("Email", context.get("email","")),
        ("Celular", context.get("celular","")),
        ("Vendedor", str(context.get("usuarioVendedor",""))),
    ]:
        if valor:
            camp = etree.SubElement(iad, "campoAdicional")
            camp.set("nombre", etiqueta)
            camp.text = str(valor)
        if context.get("direccion"):
            camp = etree.SubElement(iad, "campoAdicional", nombre="Direccion")
            camp.text = context["direccion"]

    return etree.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=False)

# ventas/utils/sri.py (PROYECTO)
import os, tempfile
from django.conf import settings
from xades_bes_sri_ec import xades
from zeep import Client, Settings

# ---------- FIRMA ----------
def firmar_xml_xades(xml_bytes: bytes) -> bytes:
    import tempfile, os
    from django.conf import settings
    from xades_bes_sri_ec import xades

    if not os.path.exists(settings.SRI_P12_PATH):
        raise FileNotFoundError(f"No existe el .p12 en: {settings.SRI_P12_PATH}")

    # normaliza CRLF y BOM, y fuerza encabezado XML si falta
    xml_bytes = xml_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    if xml_bytes.startswith(b"\xef\xbb\xbf"):
        xml_bytes = xml_bytes[3:]
    if not xml_bytes.lstrip().startswith(b"<?xml"):
        xml_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n' + xml_bytes

    ruta_in = tempfile.mktemp(suffix=".xml")
    ruta_out = tempfile.mktemp(suffix=".xml")
    with open(ruta_in, "wb") as f:
        f.write(xml_bytes)

    xades.firmar_comprobante(settings.SRI_P12_PATH, settings.SRI_P12_PASS, ruta_in, ruta_out)

    with open(ruta_out, "rb") as f:
        firmado = f.read()

    for p in (ruta_in, ruta_out):
        try: os.remove(p)
        except: pass

    if b"<ds:Signature" not in firmado or b'URI="#comprobante"' not in firmado:
        raise RuntimeError("Firma generada no parece válida (faltan nodos esperados)")

    return firmado


# ---------- SRI: Recepción y Autorización ----------
def _zeep_client(wsdl_url: str, timeout: int = 25) -> Client:
    """
    Crea un cliente zeep robusto (timeouts razonables y xml_huge_tree).
    """
    session = requests.Session()
    session.verify = True  # si tienes problemas de SSL en Windows, puedes poner False para probar
    transport = Transport(session=session, timeout=timeout)
    zset = Settings(strict=False, xml_huge_tree=True)
    return Client(wsdl=wsdl_url, settings=zset, transport=transport)


def enviar_a_recepcion(xml_firmado: bytes) -> dict:
    """
    Envía el comprobante firmado a RECEPCIÓN y devuelve dict con estado y mensajes.
    """
    cli = _zeep_client(settings.SRI_WSDL_RECEPCION)
    res = cli.service.validarComprobante(xml_firmado)

    estado = getattr(res, "estado", None)
    errores = []
    try:
        # recorrer estructura de mensajes (si falló)
        comps = getattr(res, "comprobantes", None)
        if comps and getattr(comps, "comprobante", None):
            for comp in comps.comprobante:
                if getattr(comp, "mensajes", None):
                    for m in comp.mensajes.mensaje:
                        errores.append(
                            f"{getattr(m,'identificador','?')}: {getattr(m,'mensaje','')} "
                            f"{getattr(m,'informacionAdicional','')}".strip()
                        )
    except Exception:
        pass

    return {"estado": estado, "errores": errores}


def autorizar_por_clave(clave_acceso: str) -> dict:
    """
    Consulta AUTORIZACIÓN por clave de acceso. Devuelve dict con estado y xml_autorizado (si aplica).
    """
    cli = _zeep_client(settings.SRI_WSDL_AUTORIZA)
    res = cli.service.autorizacionComprobante(clave_acceso)

    auts = getattr(res, "autorizaciones", None)
    if not auts or not getattr(auts, "autorizacion", None):
        return {"estado": "SIN_RESPUESTA", "errores": ["No hay autorizaciones en la respuesta"]}

    aut = auts.autorizacion[0]
    estado_aut = getattr(aut, "estado", None)
    if estado_aut == "AUTORIZADO":
        xml_aut = getattr(aut, "comprobante", None)  # string (XML interno)
        numero_aut = getattr(aut, "numeroAutorizacion", "")
        fecha_aut = getattr(aut, "fechaAutorizacion", "")
        return {
            "estado": "AUTORIZADO",
            "xml_autorizado": xml_aut,
            "numero_autorizacion": numero_aut,
            "fecha_autorizacion": str(fecha_aut),
        }

    # No autorizado: colectar mensajes
    errores = []
    try:
        if getattr(aut, "mensajes", None):
            for m in aut.mensajes.mensaje:
                errores.append(
                    f"{getattr(m,'identificador','?')}: {getattr(m,'mensaje','')} "
                    f"{getattr(m,'informacionAdicional','')}".strip()
                )
    except Exception:
        pass

    return {"estado": estado_aut or "NO_AUTORIZADO", "errores": errores}


def enviar_a_sri_y_autorizar(xml_firmado: bytes, clave_acceso: str) -> dict:
    """
    Flujo completo: Recepción -> Autorización.
    Retorna dict uniforme:
      ok: bool
      fase: 'recepcion'|'autorizacion'
      estado: 'RECIBIDA'|'DEVUELTA'|'AUTORIZADO'|...
      errores: [str]
      xml_autorizado (si ok)
      numero_autorizacion, fecha_autorizacion (si ok)
    """
    # 1) Recepción
    rec = enviar_a_recepcion(xml_firmado)
    if rec["estado"] != "RECIBIDA":
        return {"ok": False, "fase": "recepcion", "estado": rec["estado"], "errores": rec["errores"]}

    # 2) Autorización
    aut = autorizar_por_clave(clave_acceso)
    
    if aut["estado"] == "AUTORIZADO":
        return {"ok": True, "fase": "autorizacion", "estado": "AUTORIZADO", **aut}
    else:
        return {"ok": False, "fase": "autorizacion", "estado": aut["estado"], "errores": aut.get("errores", [])}
    
    
import base64, re, hashlib
from lxml import etree

_C14N_ALG = "http://www.w3.org/TR/2001/REC-xml-c14n-20010315"  # C14N 1.0
_SHA1_URI = "http://www.w3.org/2000/09/xmldsig#sha1"

def _c14n_1_0(element: etree._Element) -> bytes:
    # C14N 1.0, sin comentarios
    return etree.tostring(element, method="c14n", exclusive=False, with_comments=False)

def _sha1_b64(data: bytes) -> str:
    return base64.b64encode(hashlib.sha1(data).digest()).decode()

# IMPORTS (póngalos al inicio del archivo si no existen)
from lxml import etree as LET
from xades_bes_sri_ec.xades import digest_comprobante_correcto, sha1_base64

def debug_verificar_referencias(xml_firmado: bytes) -> dict:
    """
    Verifica los 3 References del SignedInfo usando EXACTAMENTE
    el mismo criterio de canonicalización que el SRI:
      - SignedProperties: C14N 1.0 del elemento con Id capturado
      - KeyInfo        : C14N 1.0 del elemento con Id capturado
      - #comprobante   : XML final menos <ds:Signature> (enveloped) y C14N 1.0 del root
    Devuelve un dict con el detalle para imprimir como 'DEBUG DIGESTS:'.
    """
    ns = {"ds": "http://www.w3.org/2000/09/xmldsig#", "etsi": "http://uri.etsi.org/01903/v1.3.2#"}
    debug = {"ok": False, "refs": []}

    try:
        root = LET.fromstring(xml_firmado)
    except Exception as e:
        return {"ok": False, "error": f"XML inválido: {e}", "refs": []}

    # 1) Ubicar SignedInfo en el XML final firmado
    si_el = root.find(".//ds:SignedInfo", namespaces=ns)
    if si_el is None:
        return {"ok": False, "error": "No se encontró ds:SignedInfo", "refs": []}

    signed_info_str = LET.tostring(si_el, encoding="utf-8").decode("utf-8")

    # 2) Extraer los expected/URI desde SignedInfo (método robusto con XPath alternativo)
    # a) SignedProperties (Type XAdES)
    sp_ref = si_el.xpath(
        ".//ds:Reference[@Type='http://uri.etsi.org/01903#SignedProperties']",
        namespaces=ns
    )
    if sp_ref:
        sp_uri = sp_ref[0].get("URI", "")
        expected_sp = (sp_ref[0].findtext(".//ds:DigestValue", namespaces=ns) or "").strip()
    else:
        sp_uri, expected_sp = None, None

    # b) KeyInfo (URI="#Certificate...")
    ki_ref = si_el.xpath(".//ds:Reference[starts-with(@URI, '#Certificate')]", namespaces=ns)
    if ki_ref:
        ki_uri = ki_ref[0].get("URI", "")
        expected_ki = (ki_ref[0].findtext(".//ds:DigestValue", namespaces=ns) or "").strip()
    else:
        ki_uri, expected_ki = None, None

    # c) Comprobante (URI="#comprobante")
    cb_ref = si_el.xpath(".//ds:Reference[@URI='#comprobante']", namespaces=ns)
    expected_cb = (cb_ref[0].findtext(".//ds:DigestValue", namespaces=ns) or "").strip() if cb_ref else None

    # 3) Calcular los calculated con el XML FINAL
    #    - SignedProperties: C14N 1.0 del nodo con Id=lo que venga tras '#'
    #    - KeyInfo        : C14N 1.0 del nodo con Id=lo que venga tras '#'
    #    - Comprobante    : digest_comprobante_correcto(xml_firmado)
    def _calc_digest_by_id(uri_fragment: str) -> str | None:
        if not uri_fragment or not uri_fragment.startswith("#"):
            return None
        frag = uri_fragment[1:]
        el = root.xpath(f"//*[@Id='{frag}']")  # Id exacto
        if not el:
            return None
        c14n = LET.tostring(el[0], method="c14n", exclusive=False, with_comments=False)
        return sha1_base64(c14n)

    calculated_sp = _calc_digest_by_id(sp_uri) if sp_uri else None
    calculated_ki = _calc_digest_by_id(ki_uri) if ki_uri else None
    calculated_cb = digest_comprobante_correcto(xml_firmado)

    # 4) Construir el detalle de depuración
    if sp_uri:
        debug["refs"].append({
            "uri": sp_uri, "ok": (expected_sp == calculated_sp),
            "expected": expected_sp, "calculated": calculated_sp
        })
    if ki_uri:
        debug["refs"].append({
            "uri": ki_uri, "ok": (expected_ki == calculated_ki),
            "expected": expected_ki, "calculated": calculated_ki
        })
    debug["refs"].append({
        "uri": "#comprobante", "ok": (expected_cb == calculated_cb),
        "expected": expected_cb, "calculated": calculated_cb
    })

    # 5) ok global si todos los refs con expected/calculated presentes están ok
    ref_oks = [r["ok"] for r in debug["refs"] if r.get("expected") and r.get("calculated")]
    debug["ok"] = (len(ref_oks) > 0 and all(ref_oks))
    return debug


# --- utils de diagnóstico de identidad del .p12 ---
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from django.conf import settings

def _extraer_serialnumber_cedula(cert):
    """
    Devuelve el valor de OID 2.5.4.5 (serialNumber) si existe (e.g. cédula),
    o None si no está presente.
    """
    try:
        for attr in cert.subject:
            if attr.oid == NameOID.SERIAL_NUMBER:
                return attr.value.strip()
    except Exception:
        pass
    return None

def diagnosticar_p12(p12_path=None, p12_pass=None, sri_ruc=None) -> dict:
    p12_path = p12_path or settings.SRI_P12_PATH
    p12_pass = p12_pass or settings.SRI_P12_PASS
    sri_ruc  = (sri_ruc or settings.SRI_RUC or "").strip()

    with open(p12_path, "rb") as fh:
        p12_bytes = fh.read()

    key, cert, chain = pkcs12.load_key_and_certificates(p12_bytes, p12_pass.encode("utf-8"))

    info = {
        "subject": cert.subject.rfc4514_string(),
        "issuer": cert.issuer.rfc4514_string(),
        "not_before": cert.not_valid_before,
        "not_after": cert.not_valid_after,
        "serial_number_hex": hex(cert.serial_number),
        "cedula_en_cert": _extraer_serialnumber_cedula(cert),
        "ruc_settings": sri_ruc,
        "coincide_persona_natural": False,
    }

    # Persona natural: RUC = cedula + "001"
    if info["cedula_en_cert"] and len(sri_ruc) == 13:
        info["coincide_persona_natural"] = (sri_ruc == (info["cedula_en_cert"] + "001"))

    return info


from signxml import XMLVerifier

def verificar_firma_local(xml_firmado: bytes, p12_path=None, p12_pass=None) -> dict:
    """
    Verifica la firma del XML con la cadena pública del .p12 localmente.
    Retorna {'ok': bool, 'error': str|None}
    """
    try:
        p12_path = p12_path or settings.SRI_P12_PATH
        p12_pass = p12_pass or settings.SRI_P12_PASS
        with open(p12_path, "rb") as fh:
            p12_bytes = fh.read()
        key, cert, chain = pkcs12.load_key_and_certificates(p12_bytes, p12_pass.encode("utf-8"))

        cert_pem = cert.public_bytes(Encoding.PEM)
        # Si tu librería XAdES no incluye la cadena completa, igual podemos verificar con el leaf:
        XMLVerifier().verify(xml_firmado, x509_cert=cert_pem)
        return {"ok": True, "error": None}
    except Exception as e:
        return {"ok": False, "error": str(e)}
