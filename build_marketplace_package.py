import os
import shutil
import zipfile

PROJECT_DIR = r"d:\otroShooter"
OUTPUT_DIR = os.path.join(PROJECT_DIR, "Marketplace_Package")
PACKAGE_ZIP = os.path.join(PROJECT_DIR, "VR_CQB_Shooter_SellMyApp_Package.zip")

print("1. Limpiando directorios previos...")
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
if os.path.exists(PACKAGE_ZIP):
    os.remove(PACKAGE_ZIP)

os.makedirs(OUTPUT_DIR, exist_ok=True)
source_dir = os.path.join(OUTPUT_DIR, "Source_Code")
doc_dir = os.path.join(OUTPUT_DIR, "Documentation")
demo_dir = os.path.join(OUTPUT_DIR, "Demo_APK")

os.makedirs(source_dir, exist_ok=True)
os.makedirs(doc_dir, exist_ok=True)
os.makedirs(demo_dir, exist_ok=True)

print("2. Copiando documentación...")
shutil.copy(os.path.join(PROJECT_DIR, "Documentation", "index.html"), os.path.join(doc_dir, "index.html"))

print("3. Copiando Demo APK...")
apk_src = os.path.join(PROJECT_DIR, "app", "build", "outputs", "apk", "debug", "app-debug.apk")
if os.path.exists(apk_src):
    shutil.copy(apk_src, os.path.join(demo_dir, "VR_CQB_Shooter_Demo.apk"))
    print("   -> APK copiado con exito.")
else:
    print("   -> ADVERTENCIA: APK no encontrado en app/build/outputs/apk/debug/app-debug.apk")

print("4. Copiando Código Fuente limpio (excluyendo temporales .gradle, build, .idea)...")
exclude_dirs = {'.gradle', '.idea', '.vscode', 'build', 'node_modules', 'Marketplace_Package', '__pycache__', '.git', 'backup_1024'}
exclude_files = {'phone_logs.txt', 'VR_CQB_Shooter_SellMyApp_Package.zip', 'package-lock.json', 'build_marketplace_package.py'}

# Copiar app
def copy_clean_dir(src, dst):
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.endswith('.log')]
        rel_path = os.path.relpath(root, src)
        dest_path = os.path.join(dst, rel_path)
        os.makedirs(dest_path, exist_ok=True)
        for f in files:
            if f not in exclude_files and not f.endswith('.log') and not f.endswith('.pyc'):
                shutil.copy2(os.path.join(root, f), os.path.join(dest_path, f))

copy_clean_dir(os.path.join(PROJECT_DIR, "app"), os.path.join(source_dir, "app"))

# Copiar archivos raíz de configuración Gradle
for f in ["build.gradle", "settings.gradle", "gradle.properties", "local.properties"]:
    src_f = os.path.join(PROJECT_DIR, f)
    if os.path.exists(src_f):
        shutil.copy2(src_f, os.path.join(source_dir, f))

# Copiar carpeta gradle wrapper
gradle_wrapper = os.path.join(PROJECT_DIR, "gradle")
if os.path.exists(gradle_wrapper):
    copy_clean_dir(gradle_wrapper, os.path.join(source_dir, "gradle"))

print("5. Empaquetando en archivo ZIP final...")
with zipfile.ZipFile(PACKAGE_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for file in files:
            abs_file = os.path.join(root, file)
            arcname = os.path.relpath(abs_file, OUTPUT_DIR)
            zipf.write(abs_file, arcname)

size_mb = os.path.getsize(PACKAGE_ZIP) / (1024 * 1024)
print(f"EXITO: Paquete creado en: {PACKAGE_ZIP} ({size_mb:.2f} MB)")
