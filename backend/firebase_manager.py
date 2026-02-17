"""
Módulo de integración con Firebase Firestore
Maneja la conexión y escritura de datos a la base de datos
"""

import os
import sys
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv


class FirebaseManager:
    """Gestor de conexión y operaciones con Firebase Firestore"""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Inicializa la conexión con Firebase.
        
        Args:
            credentials_path: Ruta al archivo de credenciales JSON.
                            Si no se proporciona, se busca automáticamente.
        """
        load_dotenv()
        
        self.credentials_path = credentials_path or self._buscar_credenciales()
        self.db = None
        self._inicializar_firebase()
    
    def _buscar_credenciales(self) -> Optional[str]:
        """Busca el archivo de credenciales en múltiples ubicaciones"""
        # 1. Variable de entorno
        env_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        if env_path and os.path.exists(env_path):
            return env_path
        
        # 2. Dentro del bundle de PyInstaller (sys._MEIPASS)
        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS
            bundled = os.path.join(base, 'config', 'firebase-credentials.json')
            if os.path.exists(bundled):
                return bundled
            # También buscar junto al ejecutable
            exe_dir = os.path.dirname(sys.executable)
            junto_exe = os.path.join(exe_dir, 'config', 'firebase-credentials.json')
            if os.path.exists(junto_exe):
                return junto_exe
        
        # 3. Relativo al archivo actual (modo desarrollo)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dev_path = os.path.join(base_dir, 'config', 'firebase-credentials.json')
        if os.path.exists(dev_path):
            return dev_path
        
        # 4. Ruta relativa al directorio de trabajo
        cwd_path = os.path.join(os.getcwd(), 'config', 'firebase-credentials.json')
        if os.path.exists(cwd_path):
            return cwd_path
        
        return None
    
    def _inicializar_firebase(self):
        """Inicializa la app de Firebase si no está inicializada"""
        if not firebase_admin._apps:
            if not self.credentials_path or not os.path.exists(self.credentials_path):
                print("⚠️ ADVERTENCIA: No se encontró archivo de credenciales Firebase.")
                print("   El sistema funcionará en modo LOCAL (sin sincronización).")
                print(f"   Ruta esperada: {self.credentials_path}")
                print("\nPara habilitar Firebase:")
                print("1. Crea un proyecto en https://console.firebase.google.com")
                print("2. Descarga las credenciales (Service Account Key)")
                print("3. Guárdalas en: config/firebase-credentials.json")
                return
            
            try:
                cred = credentials.Certificate(self.credentials_path)
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                print("✓ Firebase inicializado correctamente")
            except Exception as e:
                print(f"✗ Error inicializando Firebase: {e}")
                self.db = None
        else:
            self.db = firestore.client()
    
    def existe_viaje(self, id_viaje: str) -> bool:
        """
        Verifica si un viaje ya existe en Firestore.
        
        Args:
            id_viaje: ID del viaje a verificar
            
        Returns:
            True si el viaje ya existe
        """
        if not self.db:
            return False
        
        try:
            doc = self.db.collection('viajes').document(id_viaje).get()
            return doc.exists
        except Exception as e:
            print(f"⚠️ Error verificando existencia de viaje: {e}")
            return False
    
    def guardar_viaje(self, viaje_data: Dict) -> Optional[str]:
        """
        Guarda o actualiza un viaje en Firestore.
        
        Args:
            viaje_data: Diccionario con datos del viaje
            
        Returns:
            ID del documento creado/actualizado o None si falla
        """
        if not self.db:
            print("⚠️ Firebase no disponible. Datos no guardados.")
            return None
        
        try:
            id_viaje = viaje_data.get('id_viaje')
            if not id_viaje:
                print("✗ Error: No se proporcionó id_viaje")
                return None
            
            # Agregar metadata
            viaje_data['fecha_procesamiento'] = datetime.now().isoformat()
            viaje_data['version_sistema'] = '1.0.0'
            
            # Guardar en Firestore
            doc_ref = self.db.collection('viajes').document(id_viaje)
            doc_ref.set(viaje_data, merge=True)
            
            print(f"✓ Viaje guardado: {id_viaje}")
            return id_viaje
            
        except Exception as e:
            print(f"✗ Error guardando viaje: {e}")
            return None
    
    def guardar_lances(self, id_viaje: str, lances: List[Dict]) -> int:
        """
        Guarda los lances como subcolección del viaje.
        ELIMINA lances antiguos antes de guardar los nuevos.
        
        Args:
            id_viaje: ID del viaje padre
            lances: Lista de lances a guardar
            
        Returns:
            Número de lances guardados exitosamente
        """
        if not self.db:
            print("⚠️ Firebase no disponible. Lances no guardados.")
            return 0
        
        guardados = 0
        
        try:
            viaje_ref = self.db.collection('viajes').document(id_viaje)
            lances_collection = viaje_ref.collection('lances')
            
            # Usar batch para operación atómica (delete + insert)
            batch = self.db.batch()
            ops_count = 0
            
            # PASO 1: Marcar lances antiguos para eliminación
            lances_antiguos = lances_collection.stream()
            eliminados = 0
            for lance_doc in lances_antiguos:
                batch.delete(lance_doc.reference)
                eliminados += 1
                ops_count += 1
                # Firestore limita batches a 500 operaciones
                if ops_count >= 490:
                    batch.commit()
                    batch = self.db.batch()
                    ops_count = 0
            
            if eliminados > 0:
                print(f"  🗑️  Eliminando {eliminados} lances antiguos")
            
            # PASO 2: Agregar lances nuevos al batch
            for lance in lances:
                num_lance = lance.get('numero_lance')
                if num_lance is None:  # Permitir 0 (CAPTURA TOTAL)
                    continue
                
                lance_id = f"lance_{num_lance:03d}"
                lance_ref = lances_collection.document(lance_id)
                batch.set(lance_ref, lance)
                guardados += 1
                ops_count += 1
                if ops_count >= 490:
                    batch.commit()
                    batch = self.db.batch()
                    ops_count = 0
            
            # Commit final
            if ops_count > 0:
                batch.commit()
            
            print(f"✓ {guardados} lances guardados en {id_viaje}")
            return guardados
            
        except Exception as e:
            print(f"✗ Error guardando lances: {e}")
            import traceback
            traceback.print_exc()
            return guardados
    
    def guardar_viaje_completo(self, datos_completos: Dict) -> bool:
        """
        Guarda un viaje completo (cabecera + lances) en Firestore.
        
        Args:
            datos_completos: Resultado del parser con viaje, lances y validación
            
        Returns:
            True si se guardó correctamente
        """
        if not self.db:
            print("⚠️ Modo LOCAL: Datos no se guardarán en Firebase")
            self._guardar_local(datos_completos)
            return False
        
        try:
            # 1. Guardar viaje
            viaje_data = datos_completos.get('viaje', {})
            id_viaje = self.guardar_viaje(viaje_data)
            
            if not id_viaje:
                return False
            
            # 2. Guardar lances
            lances = datos_completos.get('lances', [])
            num_guardados = self.guardar_lances(id_viaje, lances)
            
            # 3. Guardar metadata de validación
            validacion = datos_completos.get('validacion', {})
            self.db.collection('viajes').document(id_viaje).update({
                'validacion': validacion,
                'ultima_actualizacion': datetime.now().isoformat()
            })
            
            print(f"\n{'='*50}")
            print(f"✓ VIAJE GUARDADO EN FIREBASE")
            print(f"  ID: {id_viaje}")
            print(f"  Lances: {num_guardados}")
            print(f"  Validación: {'✓' if validacion.get('es_valido') else '✗'}")
            print(f"{'='*50}\n")
            
            return True
            
        except Exception as e:
            print(f"✗ Error guardando viaje completo: {e}")
            return False
    
    def _guardar_local(self, datos_completos: Dict):
        """Guarda los datos localmente en JSON como fallback"""
        import json
        
        try:
            output_dir = "data/output"
            os.makedirs(output_dir, exist_ok=True)
            
            viaje_id = datos_completos.get('viaje', {}).get('id_viaje', 'unknown')
            filename = f"{output_dir}/{viaje_id}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(datos_completos, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Datos guardados localmente: {filename}")
            
        except Exception as e:
            print(f"✗ Error guardando localmente: {e}")
    
    def obtener_viaje(self, id_viaje: str) -> Optional[Dict]:
        """
        Obtiene un viaje desde Firestore.
        
        Args:
            id_viaje: ID del viaje a buscar
            
        Returns:
            Diccionario con datos del viaje o None
        """
        if not self.db:
            return None
        
        try:
            doc = self.db.collection('viajes').document(id_viaje).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"✗ Error obteniendo viaje: {e}")
            return None
    
    def obtener_lances_viaje(self, id_viaje: str) -> List[Dict]:
        """
        Obtiene todos los lances de un viaje.
        
        Args:
            id_viaje: ID del viaje
            
        Returns:
            Lista de lances
        """
        if not self.db:
            return []
        
        try:
            lances_ref = self.db.collection('viajes').document(id_viaje).collection('lances')
            lances = []
            
            for doc in lances_ref.stream():
                lance_data = doc.to_dict()
                lance_data['id'] = doc.id
                lances.append(lance_data)
            
            # Ordenar por número de lance
            lances.sort(key=lambda x: x.get('numero_lance', 0))
            
            return lances
            
        except Exception as e:
            print(f"✗ Error obteniendo lances: {e}")
            return []
    
    def listar_viajes(self, limite: int = 10) -> List[Dict]:
        """
        Lista los viajes más recientes.
        
        Args:
            limite: Número máximo de viajes a retornar
            
        Returns:
            Lista de viajes
        """
        if not self.db:
            return []
        
        try:
            viajes = []
            docs = self.db.collection('viajes')\
                         .order_by('fecha_zarpe', direction=firestore.Query.DESCENDING)\
                         .limit(limite)\
                         .stream()
            
            for doc in docs:
                viaje_data = doc.to_dict()
                viaje_data['id'] = doc.id
                viajes.append(viaje_data)
            
            return viajes
            
        except Exception as e:
            print(f"✗ Error listando viajes: {e}")
            return []

    def obtener_ids_viajes(self) -> set:
        """
        Obtiene el set de IDs de todos los viajes en Firestore.
        Consulta ligera que solo trae los IDs de los documentos.
        
        Returns:
            Set de IDs de viajes
        """
        if not self.db:
            return set()
        
        try:
            docs = self.db.collection('viajes').select([]).stream()
            return {doc.id for doc in docs}
        except Exception as e:
            print(f"✗ Error obteniendo IDs de viajes: {e}")
            return set()

    def obtener_info_viaje(self, id_viaje: str) -> Optional[Dict]:
        """
        Obtiene la información básica de un viaje.
        
        Args:
            id_viaje: ID del viaje
            
        Returns:
            Dict con datos del viaje o None
        """
        if not self.db:
            return None
        
        try:
            doc = self.db.collection('viajes').document(id_viaje).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception:
            return None

    def eliminar_viaje(self, id_viaje: str) -> bool:
        """
        Elimina un viaje y todos sus lances asociados de Firestore.
        
        Args:
            id_viaje: ID del viaje a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        if not self.db:
            print("✗ Firebase no conectado")
            return False
        
        try:
            # Referencia al documento del viaje
            viaje_ref = self.db.collection('viajes').document(id_viaje)
            
            # Eliminar todos los lances primero
            lances_ref = viaje_ref.collection('lances')
            lances = lances_ref.stream()
            
            lances_eliminados = 0
            for lance in lances:
                lance.reference.delete()
                lances_eliminados += 1
            
            print(f"✓ Eliminados {lances_eliminados} lances del viaje {id_viaje}")
            
            # Eliminar el documento del viaje
            viaje_ref.delete()
            
            print(f"✓ Viaje {id_viaje} eliminado correctamente de Firebase")
            return True
            
        except Exception as e:
            print(f"✗ Error eliminando viaje {id_viaje}: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ===== AUTENTICACIÓN =====
    
    # ===== REPORTES DE BUGS =====
    
    def guardar_reporte_bug(self, titulo: str, descripcion: str, seccion: str = "") -> bool:
        """
        Guarda un reporte de bug en Firebase para revisión del administrador.
        
        Args:
            titulo: Título corto del bug
            descripcion: Descripción detallada del problema
            seccion: Sección de la aplicación donde ocurrió
            
        Returns:
            True si se guardó correctamente
        """
        if not self.db:
            return False
        
        try:
            import socket
            self.db.collection('reportes_bugs').add({
                'titulo': titulo,
                'descripcion': descripcion,
                'seccion': seccion,
                'fecha': datetime.now().isoformat(),
                'estado': 'pendiente',
                'equipo': socket.gethostname()
            })
            return True
        except Exception as e:
            print(f"✗ Error guardando reporte de bug: {e}")
            return False
    
    def inicializar_credenciales(self, id_default: str = "PesqueraQuinteroSA", clave_default: str = "PQ1602SA"):
        """
        Crea las credenciales iniciales en Firebase si no existen.
        Solo se ejecuta la primera vez.
        """
        if not self.db:
            return
        
        try:
            doc = self.db.collection('config').document('auth').get()
            if not doc.exists:
                self.db.collection('config').document('auth').set({
                    'id_hash': hashlib.sha256(id_default.encode()).hexdigest(),
                    'clave_hash': hashlib.sha256(clave_default.encode()).hexdigest(),
                    'creado': datetime.now().isoformat()
                })
                print("✓ Credenciales iniciales creadas en la nube")
        except Exception as e:
            print(f"⚠️ Error inicializando credenciales: {e}")
    
    def verificar_credenciales(self, id_usuario: str, clave: str) -> bool:
        """
        Verifica credenciales de acceso contra Firebase.
        
        Args:
            id_usuario: ID de usuario proporcionado
            clave: Contraseña proporcionada
            
        Returns:
            True si las credenciales son válidas
        """
        if not self.db:
            return False
        
        try:
            doc = self.db.collection('config').document('auth').get()
            if doc.exists:
                data = doc.to_dict()
                id_hash = hashlib.sha256(id_usuario.encode()).hexdigest()
                clave_hash = hashlib.sha256(clave.encode()).hexdigest()
                return data.get('id_hash') == id_hash and data.get('clave_hash') == clave_hash
            return False
        except Exception as e:
            print(f"⚠️ Error verificando credenciales: {e}")
            return False


def test_firebase_connection():
    """Prueba la conexión con Firebase"""
    print("=== Test de Conexión Firebase ===\n")
    
    manager = FirebaseManager()
    
    if manager.db:
        print("✓ Conexión establecida")
        
        # Prueba de escritura
        test_data = {
            'id_viaje': 'TEST-2025-001',
            'nave_nombre': 'TEST',
            'estado_procesamiento': 'TEST'
        }
        
        result = manager.guardar_viaje(test_data)
        if result:
            print("✓ Escritura exitosa")
            
            # Limpiar test
            manager.db.collection('viajes').document('TEST-2025-001').delete()
            print("✓ Test completado (datos de prueba eliminados)")
        else:
            print("✗ Error en escritura")
    else:
        print("✗ No se pudo conectar a Firebase")
        print("   Revisa las credenciales en config/firebase-credentials.json")


if __name__ == "__main__":
    test_firebase_connection()
