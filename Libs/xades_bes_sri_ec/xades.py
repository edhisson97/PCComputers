from cryptography.hazmat.primitives.serialization import pkcs12
from datetime import datetime
from cryptography.x509.extensions import KeyUsage
import re
import codecs
from datetime import datetime
from OpenSSL import crypto
from .cadenas import *
import subprocess
import xml.etree.ElementTree as ET
from .utils import *
import argparse
import uuid
import os

from cryptography.hazmat.primitives.serialization import pkcs12
from OpenSSL import crypto
import xml.etree.ElementTree as ETT
from lxml import etree as LET
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding as asy_padding

MAX_LINE_SIZE = 76


def get_certificados_validos(archivo, password):
    fecha_hora_actual = datetime.now()

    private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(archivo, password)
    certificados_no_caducados = []
    certificados_validos = []

    if certificate.not_valid_after > datetime.now():
        certificados_no_caducados.append(certificate)

    for cert in additional_certificates:

        if cert.not_valid_after > fecha_hora_actual:
            certificados_no_caducados.append(cert)

    for cert in certificados_no_caducados:
        for ext in cert.extensions:

            if type(ext.value) == KeyUsage:

                if ext.value.digital_signature == True:
                    certificados_validos.append(cert)

    return certificados_validos, private_key


def get_clave_privada(ruta_p12, password):
    # https://github.com/pyca/pyopenssl/issues/770
    # No es posible recuperar con pyopenssl multiples claves_privadas
    # Se hace con una llamada directo a OPENSSL

    clave_privada_firma = None

    data = {
        'ruta': ruta_p12,
        'password': password.decode(),
    }

    CMD_OPENSSL = " openssl pkcs12  -in '{ruta}' -nocerts -passin pass:{password} -passout pass:{password} ".format(**data)

    salida_cmd = subprocess.check_output(CMD_OPENSSL, shell=True)

    salida_cmd = salida_cmd.decode()

    delimitador_inicio = '-----BEGIN ENCRYPTED PRIVATE KEY-----'
    delimitador_final = '-----END ENCRYPTED PRIVATE KEY-----'

    claves_privadas = separar_cadena(salida_cmd, delimitador_final, append_start=False)
    claves_validas = []

    for cp in claves_privadas:

        regex = '{}(.+?){}'.format(delimitador_inicio, delimitador_final)
        m = re.search(regex, cp, flags=re.DOTALL)

        if m:
            claves_validas.append(cp)

    if len(claves_validas) > 1:
        # Si la clave contiene mas de una clave privada,
        # buscar la que tenga el atributo 'Signing Key'

        for cp in claves_validas:

            if 'Signing Key' in cp:
                clave_privada_firma = cp

    elif len(claves_validas) == 1:
        clave_privada_firma = claves_validas[0]

    clave_privada_firma = separar_cadena(clave_privada_firma, delimitador_inicio, append_start=True)

    if len(clave_privada_firma) > 0:
        return clave_privada_firma[1]

    return clave_privada_firma


def get_c14n(xml_bytes_or_str) -> bytes:
    data = xml_bytes_or_str.encode("utf-8") if isinstance(xml_bytes_or_str, str) else xml_bytes_or_str
    parser = LET.XMLParser(remove_blank_text=True)
    root = LET.fromstring(data, parser=parser)
    return LET.tostring(root, method="c14n", exclusive=False, with_comments=False)

# --- Helper C14N coherente para el nodo "comprobante" ---
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding as asy_padding


XMLNS_DS = "http://www.w3.org/2000/09/xmldsig#"
XMLNS_ETSI = "http://uri.etsi.org/01903/v1.3.2#"
xmlns = f'xmlns:ds="{XMLNS_DS}" xmlns:etsi="{XMLNS_ETSI}"'

def digest_comprobante_correcto(xml_firmado_bytes: bytes) -> str:
    root = LET.fromstring(xml_firmado_bytes)
    ns = {"ds": XMLNS_DS}

    # 1) eliminar todas las ds:Signature (enveloped)
    for sig in root.xpath(".//ds:Signature", namespaces=ns):
        sig.getparent().remove(sig)

    # 2) canonicalizar el elemento raíz (ej. <factura id="comprobante">...) con C14N 1.0 sin comentarios
    c14n = LET.tostring(root, method="c14n", exclusive=False, with_comments=False)

    # 3) sha1 base64
    return sha1_base64(c14n)

def _to_bytes(x):
    return x if isinstance(x, (bytes, bytearray)) else x.encode("utf-8")

def _ensure_ns_on_tag(snippet: str, tag_qname: str, nsmap: dict) -> str:
    """
    Inserta xmlns:* faltantes en la etiqueta de apertura de 'tag_qname' (p.ej. 'ds:KeyInfo').
    nsmap: {'ds': XMLNS_DS, 'etsi': XMLNS_ETSI, ...}
    """
    if tag_qname not in snippet:
        return snippet
    missing = []
    for pfx, uri in nsmap.items():
        if f'xmlns:{pfx}=' not in snippet:
            missing.append(f'xmlns:{pfx}="{uri}"')
    if not missing:
        return snippet
    return snippet.replace(f"<{tag_qname}", f"<{tag_qname} " + " ".join(missing), 1)

def _normalize_x509_text(snippet: str) -> str:
    """
    Quita todos los espacios/saltos dentro de <ds:X509Certificate>...</ds:X509Certificate>.
    NO toca el resto. Se hace por texto para no cambiar orden/espacios de atributos.
    """
    def _compact(m):
        head, body, tail = m.group(1), m.group(2), m.group(3)
        body = re.sub(r"\s+", "", body)
        return head + body + tail

    return re.sub(
        r"(<\s*ds:X509Certificate\s*>\s*)([^<]+?)(\s*</\s*ds:X509Certificate\s*>)",
        _compact, snippet, flags=re.S
    )


def c14n_of_factura(xml_bytes: bytes) -> bytes:
    root = LET.fromstring(xml_bytes)
    el = root
    if not (el.tag.endswith("factura") and el.get("id") == "comprobante"):
        found = root.xpath("//*[@id='comprobante']")
        if not found:
            raise ValueError("No se encontró el nodo con id='comprobante'")
        el = found[0]
    return LET.tostring(el, method="c14n", exclusive=False, with_comments=False)

def c14n_factura_enveloped(xml_bytes: bytes) -> bytes:
    root = LET.fromstring(xml_bytes)
    ns = {"ds": XMLNS_DS}
    for sig in root.xpath(".//ds:Signature", namespaces=ns):
        sig.getparent().remove(sig)
    return LET.tostring(root, method="c14n", exclusive=False, with_comments=False)

def _c14n_factura_enveloped_from_str(xml_str: str) -> bytes:
    """Toma el XML final en str, remueve <ds:Signature> (enveloped) y devuelve C14N bytes de <factura>."""
    data = xml_str.encode("utf-8")
    root = LET.fromstring(data)
    ns = {"ds": XMLNS_DS}
    # elimina todas las firmas embaladas
    for sig in root.xpath(".//ds:Signature", namespaces=ns):
        sig.getparent().remove(sig)
    # c14n del root (que debe ser <factura id="comprobante">)
    return LET.tostring(root, method="c14n", exclusive=False, with_comments=False)

def get_exponente(exp_int):

    exponent = '{:X}'.format(exp_int)
    exponent = exponent.zfill(6)
    exponent = codecs.encode(codecs.decode(exponent, 'HEX'), 'BASE64').decode()
    exponent = exponent.strip()

    return exponent


def get_modulo(mod_int):

    modulo = '{:X}'.format(mod_int)

    # dividir la cadena cada 2 caracteres
    modulo = re.findall(r'(\w{2})', modulo)

    modulo = map(lambda x: chr(int(x, 16)), modulo)
    modulo = ''.join(modulo)

    modulo = encode_base64(modulo, 'LATIN-1')

    modulo = split_string_every_n(modulo, MAX_LINE_SIZE)

    return modulo


def get_certificate_x509(cert):
    certificate_pem_tmp = str(cert)

    certX509 = re.findall(
        r"-----BEGIN CERTIFICATE-----(.*?)-----END CERTIFICATE-----",
        certificate_pem_tmp, flags=re.DOTALL
    )

    certX509 = certX509[0].replace('\n', '').replace('\\n', '')

    certX509 = split_string_every_n(certX509, MAX_LINE_SIZE)

    return certX509



def _append_chain_to_key_info(key_info_xml: str, chain_openssl: list) -> str:
    """Inserta <ds:X509Certificate> para la cadena completa dentro de <ds:X509Data>."""
    if not chain_openssl:
        return key_info_xml
    extras = []
    for cert in chain_openssl:
        der = crypto.dump_certificate(crypto.FILETYPE_ASN1, cert)
        b64 = encode_base64(der)
        extras.append(f"<ds:X509Certificate>{b64}</ds:X509Certificate>")
    return key_info_xml.replace("</ds:X509Data>", "".join(extras) + "</ds:X509Data>")

def procesar_firmar_comprobante(archivo_p12: bytes, password: bytes, xml: bytes, ruta_xml_auth: str):
    """
    - archivo_p12: bytes del .p12
    - password   : bytes (utf-8)
    - xml        : bytes UTF-8 del comprobante sin firmar (con o sin <?xml ...?>)
    - ruta_xml_auth: ruta destino del XML firmado
    """
    # 1) Cargar .p12 (cryptography)
    private_key, certificate, additional = pkcs12.load_key_and_certificates(archivo_p12, password)
    if certificate is None:
        raise ValueError("El .p12 no contiene certificado principal")

    # 2) Convertir a OpenSSL (para dumps y cadena)
    cert_openssl = crypto.X509.from_cryptography(certificate)
    chain_openssl = [crypto.X509.from_cryptography(c) for c in (additional or [])]

    # 3) XML siempre como BYTES
    #xml_bytes = _to_bytes(xml)

    # --- 3.5) Placeholder para simular firma (antes del digest del comprobante) ---
    SIG_PLACEHOLDER = (
        '<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" '
        'xmlns:etsi="http://uri.etsi.org/01903/v1.3.2#"></ds:Signature>'
    )

    # --- 4) Digest del comprobante considerando transform enveloped (preview con placeholder) ---
    xml_str_clean = xml.decode("utf-8")
    if xml_str_clean.lstrip().startswith("<?xml"):
        xml_str_clean = xml_str_clean.split("?>", 1)[1]

    # Identificar el tag raíz del comprobante (factura, notaCredito, etc.)
    import lxml.etree as ETT
    root_tag = ETT.fromstring(xml_str_clean.encode("utf-8")).tag
    local_root = root_tag.split('}', 1)[-1]
    tail_tag = f"</{local_root}>"

    # Inserta la firma vacía justo antes del cierre del root (para simular el contexto real)
    xml_preview_str = xml_str_clean.replace(tail_tag, SIG_PLACEHOLDER + tail_tag)
    xml_preview_bytes = xml_preview_str.encode("utf-8")

    # Aplica la canonicalización y transform enveloped sobre el XML con placeholder
    xml_c14n_comprobante = c14n_factura_enveloped(xml_preview_bytes)
    sha1_comprobante = sha1_base64(xml_c14n_comprobante)
    
    # Tras construir xml_preview_bytes:
    print("DBG len(preview factura c14n):", len(xml_c14n_comprobante))
    print("DBG sha1(preview factura c14n):", sha1_comprobante)
    
    # 5) Datos del certificado
    certificate_pem = crypto.dump_certificate(crypto.FILETYPE_PEM, cert_openssl)
    cert_for_x509data = get_certificate_x509(certificate_pem)  # string XML de <ds:X509Data>...
    cert_pem = crypto.load_certificate(crypto.FILETYPE_PEM, certificate_pem)
    cert_der = crypto.dump_certificate(crypto.FILETYPE_ASN1, cert_pem)
    certificate_der_hash = sha1_base64(cert_der)               # bytes OK

    pub_nums = certificate.public_key().public_numbers()
    modulo = get_modulo(pub_nums.n)
    exponente = get_exponente(pub_nums.e)

    serial_number = cert_pem.get_serial_number()
    issuer_name = cert_pem.get_issuer()
    issuer_name = "".join(",{0:s}={1:s}".format(name.decode(), value.decode())
                          for name, value in issuer_name.get_components())
    if issuer_name.startswith(","):
        issuer_name = issuer_name[1:]

    # 6) IDs pseudo-aleatorios
    certificate_number = p_obtener_aleatorio()
    signature_number = p_obtener_aleatorio()
    signed_properties_number = p_obtener_aleatorio()
    signed_info_number = p_obtener_aleatorio()
    signed_properties_id_number = p_obtener_aleatorio()
    reference_id_number = p_obtener_aleatorio()
    signature_value_number = p_obtener_aleatorio()
    object_number = p_obtener_aleatorio()

    # 7) SignedProperties (XAdES-BES) y su digest  [REEMPLAZO COMPLETO]
    signed_properties = get_signed_properties(
        signature_number, signed_properties_number,
        certificate_der_hash, serial_number, reference_id_number, issuer_name
    )

    # Asegurar que el nodo usado para hash ES EL MISMO que insertaremos
    # (misma etiqueta y mismos xmlns en la apertura)
    signed_properties = _ensure_ns_on_tag(
        signed_properties,
        "etsi:SignedProperties",
        {"ds": XMLNS_DS, "etsi": XMLNS_ETSI}
    )

    # C14N *del mismo string* que se insertará en el XML
    sp_c14n = get_c14n(signed_properties)
    if isinstance(sp_c14n, str):
        sp_c14n = sp_c14n.encode("utf-8")
    sha1_signed_properties = sha1_base64(sp_c14n)

    # 8) KeyInfo (principal + cadena), normaliza X509 y calcula digest C14N
    key_info = get_key_info(certificate_number, cert_for_x509data, modulo, exponente)
    key_info = _append_chain_to_key_info(key_info, chain_openssl)

    key_info_for_hash = _ensure_ns_on_tag(
        key_info, "ds:KeyInfo", {"ds": XMLNS_DS, "etsi": XMLNS_ETSI}
    )
    key_info_for_hash = _normalize_x509_text(key_info_for_hash)

    # Construir elemento y fijar Id coherente
    ki_elem = LET.fromstring(key_info_for_hash.encode("utf-8"))
    if ki_elem.get("Id") != f"Certificate{certificate_number}":
        ki_elem.set("Id", f"Certificate{certificate_number}")

    # Re-serializar para insertar (cadena FINAL a incrustar)
    key_info = LET.tostring(ki_elem, encoding="utf-8").decode("utf-8")

    # Digest sobre C14N del KeyInfo ya normalizado y con Id correcto
    ki_c14n = LET.tostring(ki_elem, method="c14n", exclusive=False, with_comments=False)
    sha1_certificado = sha1_base64(ki_c14n)

        # 9) SignedInfo (todavía sin firmar)
    signed_info = get_signed_info(
        signed_info_number, signed_properties_id_number, sha1_signed_properties,
        certificate_number, sha1_certificado,
        reference_id_number, sha1_comprobante,
        signature_number, signed_properties_number
    )

    # --- 10) Construir <ds:Signature> XAdES-BES con SignatureValue de prueba ---
    SIGN_PLACEHOLDER = "__SIGNATURE_PLACEHOLDER__"

    xades_bes = get_xades_bes(
        xmlns,
        signature_number,
        signature_value_number,
        object_number,
        signed_info,
        SIGN_PLACEHOLDER,   # <ds:SignatureValue> aún sin la firma real
        key_info,
        signed_properties,
    )

    # Asegura xmlns solo en la raíz de <ds:Signature>
    xades_bes = _ensure_ns_on_tag(xades_bes, "ds:Signature", {"ds": XMLNS_DS, "etsi": XMLNS_ETSI})

    # --- 11) Canonicalizar el SignedInfo EXACTO que quedará en el XML ---
    sig_root = LET.fromstring(xades_bes.encode("utf-8"))
    ns = {"ds": XMLNS_DS}
    signed_info_el = sig_root.find("ds:SignedInfo", namespaces=ns)
    si_for_sign = LET.tostring(
        signed_info_el,
        method="c14n",
        exclusive=False,
        with_comments=False,
    )

    print("DBG len(SignedInfo c14n):", len(si_for_sign))
    print("DBG SHA1(SignedInfo c14n):", sha1_base64(si_for_sign))

    # --- 12) Firmar RSA/SHA1 sobre esos bytes ---
    signature_raw = private_key.sign(si_for_sign, asy_padding.PKCS1v15(), hashes.SHA1())
    signature_b64 = encode_base64(signature_raw).strip().replace("\n", "").replace("\r", "")

    # --- 13) Reemplazar el placeholder con la firma real ---
    xades_bes = xades_bes.replace(SIGN_PLACEHOLDER, signature_b64)

        # --- 14) (Opcional) Compactar SOLO el contenido de <ds:SignatureValue>, como ya tenía ---
    xades_bes = re.sub(
        r"(<\s*ds:SignatureValue\s*>)([\s\S]*?)(<\s*/\s*ds:SignatureValue\s*>)",
        lambda m: m.group(1) + m.group(2).strip().replace("\n","").replace("\r","") + m.group(3),
        xades_bes,
    )

    # --- 15) Construir el XML firmado (insertar <ds:Signature> antes del cierre del root) ---
    xml_str = xml.decode("utf-8")
    if xml_str.lstrip().startswith("<?xml"):
        xml_str = xml_str.split("?>", 1)[1]
    xml_str = xml_str.rstrip()

    root_tag = ETT.fromstring(xml_str).tag
    local = root_tag.split('}', 1)[-1]   # si viene {ns}factura -> factura
    tail_tag = f"</{local}>"

    xml_firmado_str = xml_str.replace(tail_tag, xades_bes + tail_tag)
    final_bytes = xml_firmado_str.encode("utf-8")

    # ============================================================
    #  COMPROBACIÓN 2: DEBUG DIGESTS (propio)  -> AQUÍ VA EL BLOQUE
    # ============================================================
    debug = {"ok": False, "refs": []}

    # a) SignedProperties
    m_sp = re.search(
        r'<ds:Reference[^>]+Type="http://uri\.etsi\.org/01903#SignedProperties"[^>]+URI="#([^"]+)"[\s\S]*?<ds:DigestValue>([^<]+)</ds:DigestValue>',
        signed_info
    )
    if m_sp:
        uri_sp, expected_sp = "#" + m_sp.group(1), m_sp.group(2).strip()
    else:
        uri_sp, expected_sp = "#(no encontrado)", None

    # b) KeyInfo
    m_ki = re.search(
        r'<ds:Reference[^>]+URI="#(Certificate[^"]+)"[\s\S]*?<ds:DigestValue>([^<]+)</ds:DigestValue>',
        signed_info
    )
    if m_ki:
        uri_ki, expected_ki = "#" + m_ki.group(1), m_ki.group(2).strip()
    else:
        uri_ki, expected_ki = "#(no encontrado)", None

    # c) Comprobante
    m_cb = re.search(
        r'<ds:Reference[^>]+URI="#comprobante"[\s\S]*?<ds:DigestValue>([^<]+)</ds:DigestValue>',
        signed_info
    )
    expected_cb = m_cb.group(1).strip() if m_cb else None

    # Cálculos "calculated"
    calculated_sp = sha1_signed_properties
    calculated_ki = sha1_certificado
    calculated_cb = digest_comprobante_correcto(final_bytes)

    debug["refs"].append({
        "uri": uri_sp,
        "ok": (expected_sp == calculated_sp),
        "expected": expected_sp,
        "calculated": calculated_sp,
    })
    debug["refs"].append({
        "uri": uri_ki,
        "ok": (expected_ki == calculated_ki),
        "expected": expected_ki,
        "calculated": calculated_ki,
    })
    debug["refs"].append({
        "uri": "#comprobante",
        "ok": (expected_cb == calculated_cb),
        "expected": expected_cb,
        "calculated": calculated_cb,
    })

    debug["ok"] = all(r.get("ok") for r in debug["refs"] if r["expected"] and r["calculated"])
    print("DEBUG DIGESTS (PROPIO):", debug)

    # ============================================================
    #  COMPARACIÓN PREVIEW vs FINAL (como ya tenía)
    # ============================================================
    preview_bytes = (xml_str.replace(
        tail_tag,
        '<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" '
        'xmlns:etsi="http://uri.etsi.org/01903/v1.3.2#"></ds:Signature>' + tail_tag
    )).encode("utf-8")

    sha_preview = sha1_base64(c14n_factura_enveloped(preview_bytes))
    sha_final   = sha1_base64(c14n_factura_enveloped(final_bytes))

    print("DBG sha1(preview factura c14n):", sha_preview)
    print("DBG sha1(final   factura c14n):", sha_final)
    print("DBG MATCH preview vs final:", sha_preview == sha_final)

    with open(ruta_xml_auth, "wb") as fo:
        fo.write(final_bytes)

    return final_bytes



def firmar_comprobante(ruta_p12, password, ruta_xml, ruta_xml_auth):
    """
    Firma el XML en ruta_xml y escribe el firmado en ruta_xml_auth.
    Lee .p12 y XML como BYTES y delega a procesar_firmar_comprobante.
    """
    with open(ruta_p12, "rb") as fp:
        archivo_p12 = fp.read()
    with open(ruta_xml, "rb") as fx:
        xml = fx.read()

    if isinstance(password, str):
        password = password.encode("utf-8")

    # Import local para evitar ciclos
    from xades_bes_sri_ec.xades import procesar_firmar_comprobante
    procesar_firmar_comprobante(archivo_p12, password, xml, ruta_xml_auth)


def get_signed_info(
    signed_info_number: int,
    signed_properties_id_number: int,
    sha1_signed_properties: str,
    certificate_number: int,
    sha1_certificado: str,
    reference_id_number: int,
    sha1_comprobante: str,
    signature_number: int,
    signed_properties_number: int,
) -> str:
    """
    Construye <ds:SignedInfo> con:
      - CanonicalizationMethod: C14N 1.0 (no exclusive, sin comentarios)
      - SignatureMethod: RSA-SHA1   (SRI)
      - Reference a SignedProperties (Type XAdES, Digest SHA1)
      - Reference a KeyInfo         (Digest SHA1)
      - Reference a #comprobante con Transforms:
            - enveloped-signature
            - c14n 1.0 (no exclusive)
        y Digest SHA1.
    """
    XMLNS_DS   = "http://www.w3.org/2000/09/xmldsig#"
    XMLNS_ETSI = "http://uri.etsi.org/01903/v1.3.2#"

    # IMPORTANTE: C14N 1.0 no exclusiva, sin comentarios
    can_method = "http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
    sig_method = "http://www.w3.org/2000/09/xmldsig#rsa-sha1"
    dig_method = "http://www.w3.org/2000/09/xmldsig#sha1"
    trans_enveloped = "http://www.w3.org/2000/09/xmldsig#enveloped-signature"

    # Referencia a SignedProperties (XAdES)
    ref_signed_props = f"""
    <ds:Reference Id="SignedPropertiesID{signed_properties_id_number}"
                  Type="http://uri.etsi.org/01903#SignedProperties"
                  URI="#Signature{signature_number}-SignedProperties{signed_properties_number}">
        <ds:DigestMethod Algorithm="{dig_method}"/>
        <ds:DigestValue>{sha1_signed_properties}</ds:DigestValue>
    </ds:Reference>""".strip()

    # Referencia a KeyInfo
    ref_key_info = f"""
    <ds:Reference Id="ReferenceKeyInfo{certificate_number}" URI="#Certificate{certificate_number}">
        <ds:DigestMethod Algorithm="{dig_method}"/>
        <ds:DigestValue>{sha1_certificado}</ds:DigestValue>
    </ds:Reference>""".strip()

    # Referencia al comprobante (OJO: Transforms correctos)
    ref_comprobante = f"""
    <ds:Reference Id="ReferenceID{reference_id_number}" URI="#comprobante">
        <ds:Transforms>
            <ds:Transform Algorithm="{trans_enveloped}"/>
            <ds:Transform Algorithm="{can_method}"/>
        </ds:Transforms>
        <ds:DigestMethod Algorithm="{dig_method}"/>
        <ds:DigestValue>{sha1_comprobante}</ds:DigestValue>
    </ds:Reference>""".strip()

    signed_info = f"""
<ds:SignedInfo Id="Signature-SignedInfo{signed_info_number}">
    <ds:CanonicalizationMethod Algorithm="{can_method}"/>
    <ds:SignatureMethod Algorithm="{sig_method}"/>
    {ref_signed_props}
    {ref_key_info}
    {ref_comprobante}
</ds:SignedInfo>""".strip()

    return signed_info


