from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
import hashlib

# ---------- CONFIGURACIÓN ----------
SECRET_KEY = "clave-super-secreta-para-jwt"
ALGORITHM = "HS256"
security = HTTPBearer()

app = FastAPI(title="API Sistema de Gestión Hospitalaria")

# CORS para Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- MODELOS Pydantic ----------
class Paciente(BaseModel):
    id: Optional[int] = None
    nombre: str
    apellido: str
    fecha_nacimiento: str  # "YYYY-MM-DD"
    genero: str  # "M" o "F"
    telefono: str
    direccion: str = ""
    responsable_legal_id: Optional[int] = None  # para menores

class Medico(BaseModel):
    id: Optional[int] = None
    nombre: str
    apellido: str
    especialidad: str
    num_colegiatura: str
    horario: str  # ej: "08:00-17:00"

class Cita(BaseModel):
    id: Optional[int] = None
    paciente_id: int
    medico_id: int
    fecha_hora: str  # "YYYY-MM-DD HH:MM:SS"
    motivo: str
    estado: str = "programada"  # programada, completada, cancelada

class Consulta(BaseModel):
    id: Optional[int] = None
    cita_id: int
    diagnostico: str
    tratamiento: str = ""
    notas: str = ""
    tiempo_registro: int  # segundos, debe ser <= 300

class Receta(BaseModel):
    id: Optional[int] = None
    consulta_id: int
    fecha_emision: str = ""  # se genera automático
    firma_electronica: str = ""  # se genera con hash
    vigente: bool = True

class Medicamento(BaseModel):
    id: Optional[int] = None
    nombre: str
    presentacion: str
    concentracion: str
    stock: int
    stock_minimo: int

class DetalleReceta(BaseModel):
    id: Optional[int] = None
    receta_id: int
    medicamento_id: int
    cantidad: int
    indicaciones: str = ""

class Examen(BaseModel):
    id: Optional[int] = None
    paciente_id: int
    medico_solicitante_id: int
    fecha_solicitud: str = ""  # auto
    fecha_realizacion: str = ""
    resultado: str = ""
    archivo_resultado: str = ""  # URL o nombre de archivo
    estado: str = "pendiente"  # pendiente, completado, critico

class Factura(BaseModel):
    id: Optional[int] = None
    paciente_id: int
    cita_id: int
    fecha_emision: str = ""  # auto
    monto_total: float
    estado_pago: str = "pendiente"  # pagada, pendiente
    metodo_pago: str = ""

class Pago(BaseModel):
    id: Optional[int] = None
    factura_id: int
    fecha_pago: str = ""  # auto
    monto: float
    referencia: str = ""

# ---------- BASE DE DATOS SIMULADA ----------
db = {
    "pacientes": [],
    "medicos": [],
    "citas": [],
    "consultas": [],
    "recetas": [],
    "medicamentos": [],
    "detalle_recetas": [],
    "examenes": [],
    "facturas": [],
    "pagos": [],
    "bitacora": [],
}
# IDs autoincrementales
counters = {k: 0 for k in db.keys()}

# ---------- AUTENTICACIÓN JWT ----------
def crear_token(username: str):
    payload = {"sub": username, "exp": datetime.utcnow() + timedelta(hours=2)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

# ---------- ENDPOINTS PÚBLICOS ----------
@app.post("/login")
def login(username: str, password: str):
    # Simulación: solo admin/admin123
    if username == "admin" and password == "admin123":
        token = crear_token(username)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")

# ---------- PACIENTES ----------
@app.get("/pacientes", response_model=List[Paciente])
def listar_pacientes(_=Depends(verificar_token)):
    return db["pacientes"]

@app.post("/pacientes", response_model=Paciente, status_code=201)
def crear_paciente(paciente: Paciente, _=Depends(verificar_token)):
    counters["pacientes"] += 1
    paciente.id = counters["pacientes"]
    # Validar que el responsable legal exista si se especifica
    if paciente.responsable_legal_id:
        if not any(p.id == paciente.responsable_legal_id for p in db["pacientes"]):
            raise HTTPException(404, "Responsable legal no encontrado")
    db["pacientes"].append(paciente)
    return paciente

@app.get("/pacientes/{id}", response_model=Paciente)
def obtener_paciente(id: int, _=Depends(verificar_token)):
    for p in db["pacientes"]:
        if p.id == id:
            return p
    raise HTTPException(404, "Paciente no encontrado")

@app.put("/pacientes/{id}", response_model=Paciente)
def actualizar_paciente(id: int, paciente: Paciente, _=Depends(verificar_token)):
    for i, p in enumerate(db["pacientes"]):
        if p.id == id:
            paciente.id = id
            db["pacientes"][i] = paciente
            return paciente
    raise HTTPException(404, "Paciente no encontrado")

@app.delete("/pacientes/{id}")
def eliminar_paciente(id: int, _=Depends(verificar_token)):
    for i, p in enumerate(db["pacientes"]):
        if p.id == id:
            del db["pacientes"][i]
            return {"mensaje": "Paciente eliminado"}
    raise HTTPException(404, "Paciente no encontrado")

# ---------- MÉDICOS ----------
@app.get("/medicos", response_model=List[Medico])
def listar_medicos(_=Depends(verificar_token)):
    return db["medicos"]

@app.post("/medicos", response_model=Medico, status_code=201)
def crear_medico(medico: Medico, _=Depends(verificar_token)):
    counters["medicos"] += 1
    medico.id = counters["medicos"]
    db["medicos"].append(medico)
    return medico

@app.put("/medicos/{id}", response_model=Medico)
def actualizar_medico(id: int, medico: Medico, _=Depends(verificar_token)):
    for i, m in enumerate(db["medicos"]):
        if m.id == id:
            medico.id = id
            db["medicos"][i] = medico
            return medico
    raise HTTPException(404, "Médico no encontrado")

@app.delete("/medicos/{id}")
def eliminar_medico(id: int, _=Depends(verificar_token)):
    for i, m in enumerate(db["medicos"]):
        if m.id == id:
            del db["medicos"][i]
            return {"mensaje": "Médico eliminado"}
    raise HTTPException(404, "Médico no encontrado")

# ---------- CITAS (con validación de duplicado) ----------
@app.get("/citas", response_model=List[Cita])
def listar_citas(_=Depends(verificar_token)):
    return db["citas"]

@app.post("/citas", response_model=Cita, status_code=201)
def crear_cita(cita: Cita, _=Depends(verificar_token)):
    # Validar existencia de paciente y médico
    if not any(p.id == cita.paciente_id for p in db["pacientes"]):
        raise HTTPException(404, "Paciente no encontrado")
    if not any(m.id == cita.medico_id for m in db["medicos"]):
        raise HTTPException(404, "Médico no encontrado")
    # Restricción: no dos citas del mismo paciente con el mismo médico a la misma hora
    for c in db["citas"]:
        if c.paciente_id == cita.paciente_id and c.medico_id == cita.medico_id and c.fecha_hora == cita.fecha_hora:
            raise HTTPException(409, "El paciente ya tiene una cita con este médico a esa hora")
    counters["citas"] += 1
    cita.id = counters["citas"]
    cita.estado = "programada"
    db["citas"].append(cita)
    return cita

@app.put("/citas/{id}", response_model=Cita)
def actualizar_cita(id: int, cita: Cita, _=Depends(verificar_token)):
    for i, c in enumerate(db["citas"]):
        if c.id == id:
            cita.id = id
            db["citas"][i] = cita
            return cita
    raise HTTPException(404, "Cita no encontrada")

@app.delete("/citas/{id}")
def cancelar_cita(id: int, _=Depends(verificar_token)):
    for i, c in enumerate(db["citas"]):
        if c.id == id:
            if c.estado == "completada":
                raise HTTPException(400, "No se puede cancelar una cita completada")
            del db["citas"][i]
            return {"mensaje": "Cita cancelada"}
    raise HTTPException(404, "Cita no encontrada")

# ---------- CONSULTAS (con límite de tiempo) ----------
@app.get("/consultas", response_model=List[Consulta])
def listar_consultas(_=Depends(verificar_token)):
    return db["consultas"]

@app.post("/consultas", response_model=Consulta, status_code=201)
def crear_consulta(consulta: Consulta, _=Depends(verificar_token)):
    if consulta.tiempo_registro > 300:
        raise HTTPException(400, "El tiempo de registro excede los 5 minutos permitidos")
    # Validar que la cita existe y está completada
    cita = next((c for c in db["citas"] if c.id == consulta.cita_id), None)
    if not cita:
        raise HTTPException(404, "Cita no encontrada")
    if cita.estado != "completada":
        raise HTTPException(400, "La cita debe estar completada para registrar una consulta")
    counters["consultas"] += 1
    consulta.id = counters["consultas"]
    db["consultas"].append(consulta)
    return consulta

# ---------- RECETAS ----------
@app.get("/recetas", response_model=List[Receta])
def listar_recetas(_=Depends(verificar_token)):
    return db["recetas"]

@app.post("/recetas", response_model=Receta, status_code=201)
def crear_receta(receta: Receta, _=Depends(verificar_token)):
    # Validar que la consulta existe
    if not any(c.id == receta.consulta_id for c in db["consultas"]):
        raise HTTPException(404, "Consulta no encontrada")
    counters["recetas"] += 1
    receta.id = counters["recetas"]
    receta.fecha_emision = datetime.now().strftime("%Y-%m-%d")
    receta.firma_electronica = hashlib.sha256(f"{receta.consulta_id}{receta.fecha_emision}".encode()).hexdigest()
    db["recetas"].append(receta)
    return receta

# ---------- MEDICAMENTOS ----------
@app.get("/medicamentos", response_model=List[Medicamento])
def listar_medicamentos(_=Depends(verificar_token)):
    return db["medicamentos"]

@app.post("/medicamentos", response_model=Medicamento, status_code=201)
def crear_medicamento(med: Medicamento, _=Depends(verificar_token)):
    counters["medicamentos"] += 1
    med.id = counters["medicamentos"]
    db["medicamentos"].append(med)
    return med

@app.put("/medicamentos/{id}/stock")
def actualizar_stock(id: int, stock: int, _=Depends(verificar_token)):
    for m in db["medicamentos"]:
        if m.id == id:
            m.stock = stock
            if m.stock < m.stock_minimo:
                # Aquí se podría enviar alerta (simulación)
                print(f"ALERTA: stock bajo de {m.nombre}")
            return {"mensaje": "Stock actualizado", "stock": m.stock}
    raise HTTPException(404, "Medicamento no encontrado")

# ---------- DETALLE RECETAS ----------
@app.get("/detalle_recetas", response_model=List[DetalleReceta])
def listar_detalle_recetas(_=Depends(verificar_token)):
    return db["detalle_recetas"]

@app.post("/detalle_recetas", response_model=DetalleReceta, status_code=201)
def crear_detalle_receta(detalle: DetalleReceta, _=Depends(verificar_token)):
    # Validar receta y medicamento
    if not any(r.id == detalle.receta_id for r in db["recetas"]):
        raise HTTPException(404, "Receta no encontrada")
    if not any(m.id == detalle.medicamento_id for m in db["medicamentos"]):
        raise HTTPException(404, "Medicamento no encontrado")
    counters["detalle_recetas"] += 1
    detalle.id = counters["detalle_recetas"]
    db["detalle_recetas"].append(detalle)
    return detalle

# ---------- EXÁMENES ----------
@app.get("/examenes", response_model=List[Examen])
def listar_examenes(_=Depends(verificar_token)):
    return db["examenes"]

@app.post("/examenes", response_model=Examen, status_code=201)
def crear_examen(examen: Examen, _=Depends(verificar_token)):
    # Validar paciente y médico
    if not any(p.id == examen.paciente_id for p in db["pacientes"]):
        raise HTTPException(404, "Paciente no encontrado")
    if not any(m.id == examen.medico_solicitante_id for m in db["medicos"]):
        raise HTTPException(404, "Médico no encontrado")
    counters["examenes"] += 1
    examen.id = counters["examenes"]
    examen.fecha_solicitud = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db["examenes"].append(examen)
    # Si es crítico, enviar notificación (simulación)
    if examen.estado == "critico":
        print(f"ALERTA: resultado crítico para paciente {examen.paciente_id}")
    return examen

@app.put("/examenes/{id}/resultado")
def actualizar_resultado_examen(id: int, resultado: str, estado: str, _=Depends(verificar_token)):
    for e in db["examenes"]:
        if e.id == id:
            e.resultado = resultado
            e.estado = estado
            e.fecha_realizacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if estado == "critico":
                print(f"ALERTA: resultado crítico para examen {id}")
            return {"mensaje": "Examen actualizado"}
    raise HTTPException(404, "Examen no encontrado")

# ---------- FACTURAS (con validación de deuda) ----------
@app.get("/facturas", response_model=List[Factura])
def listar_facturas(_=Depends(verificar_token)):
    return db["facturas"]

@app.post("/facturas", response_model=Factura, status_code=201)
def crear_factura(factura: Factura, _=Depends(verificar_token)):
    # Validar paciente y cita
    if not any(p.id == factura.paciente_id for p in db["pacientes"]):
        raise HTTPException(404, "Paciente no encontrado")
    if not any(c.id == factura.cita_id for c in db["citas"]):
        raise HTTPException(404, "Cita no encontrada")
    # Restricción: no emitir factura si el paciente tiene deudas pendientes
    deuda_pendiente = any(f.paciente_id == factura.paciente_id and f.estado_pago == "pendiente" for f in db["facturas"])
    if deuda_pendiente:
        raise HTTPException(400, "El paciente tiene deudas pendientes, no se puede emitir factura")
    counters["facturas"] += 1
    factura.id = counters["facturas"]
    factura.fecha_emision = datetime.now().strftime("%Y-%m-%d")
    db["facturas"].append(factura)
    return factura

# ---------- PAGOS ----------
@app.get("/pagos", response_model=List[Pago])
def listar_pagos(_=Depends(verificar_token)):
    return db["pagos"]

@app.post("/pagos", response_model=Pago, status_code=201)
def registrar_pago(pago: Pago, _=Depends(verificar_token)):
    # Validar factura
    factura = next((f for f in db["facturas"] if f.id == pago.factura_id), None)
    if not factura:
        raise HTTPException(404, "Factura no encontrada")
    if factura.estado_pago == "pagada":
        raise HTTPException(400, "La factura ya está pagada")
    counters["pagos"] += 1
    pago.id = counters["pagos"]
    pago.fecha_pago = datetime.now().strftime("%Y-%m-%d")
    db["pagos"].append(pago)
    # Actualizar estado de factura si se completó el pago
    total_pagado = sum(p.monto for p in db["pagos"] if p.factura_id == factura.id)
    if total_pagado >= factura.monto_total:
        factura.estado_pago = "pagada"
    return pago

# ---------- BITÁCORA (auditoría) ----------
@app.get("/bitacora")
def ver_bitacora(_=Depends(verificar_token)):
    return db["bitacora"]

# ---------- REPORTES ----------
@app.get("/reportes/ingresos")
def reporte_ingresos(_=Depends(verificar_token)):
    total = sum(f.monto_total for f in db["facturas"] if f.estado_pago == "pagada")
    return {"total_ingresos": total}

# ---------- INICIO ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)