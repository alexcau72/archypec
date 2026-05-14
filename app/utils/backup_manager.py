import shutil
import os
from datetime import datetime

class BackupManager:
    @staticmethod
    def create_full_backup(source_dir='.', backup_root='backups'):
        if not os.path.exists(backup_root):
            os.makedirs(backup_root)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"archypec_backup_{timestamp}"

        temp_dir = f"temp_backup_{timestamp}"

        def ignore_patterns(path, names):
            ignored = []
            if 'backups' in names: ignored.append('backups')
            if '__pycache__' in names: ignored.append('__pycache__')
            if '.git' in names: ignored.append('.git')
            # Critical: ignore the temp_dir itself if it's in the current directory
            if temp_dir in names: ignored.append(temp_dir)
            return ignored

        try:
            shutil.copytree(source_dir, temp_dir, ignore=ignore_patterns)
            shutil.make_archive(backup_name, 'zip', temp_dir)

            final_path = os.path.join(backup_root, f"{backup_name}.zip")
            shutil.move(f"{backup_name}.zip", final_path)
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

        return final_path
