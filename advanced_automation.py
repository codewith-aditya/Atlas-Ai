import os
import shutil
import glob
from datetime import datetime

# ============================================================================
# DEEP SYSTEM CONTROL MODULE
# ============================================================================

def organize_directory(path):
    """
    Organize files in the given directory into categorized folders.
    Start with Downloads or Documents.
    Categories: Images, Videos, Documents, Archives, Music, Programs
    """
    if not os.path.exists(path):
        return f"Directory not found: {path}"

    stats = {"moved": 0, "errors": 0}
    
    # Define categories
    extensions = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
        "Videos": [".mp4", ".mkv", ".flv", ".avi", ".mov", ".wmv"],
        "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Music": [".mp3", ".wav", ".aac", ".flac"],
        "Programs": [".exe", ".msi", ".bat", ".py", ".iso"]
    }

    try:
        # Create folders if they don't exist
        for category in extensions:
            folder_path = os.path.join(path, category)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

        # Move files
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
                
            file_ext = os.path.splitext(filename)[1].lower()
            
            moved = False
            for category, exts in extensions.items():
                if file_ext in exts:
                    target_folder = os.path.join(path, category)
                    target_path = os.path.join(target_folder, filename)
                    
                    # Handle duplicate names
                    if os.path.exists(target_path):
                        base, ext = os.path.splitext(filename)
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        target_path = os.path.join(target_folder, f"{base}_{timestamp}{ext}")
                    
                    shutil.move(file_path, target_path)
                    stats["moved"] += 1
                    moved = True
                    break
            
            # Optional: Move unknown files to 'Others'
            # if not moved: ...

        return f"Organization complete. Moved {stats['moved']} files."

    except Exception as e:
        return f"Error organizing directory: {str(e)}"

def clean_temp_files():
    """
    Clean system temporary files to free up space.
    Targets: User Temp folder, Windows Temp (if admin), Prefetch (if admin)
    """
    temp_folders = [
        os.environ.get('TEMP'),  # User Temp
        os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp'), # Windows Temp
    ]
    
    deleted_count = 0
    bytes_freed = 0
    
    for folder in temp_folders:
        if not folder or not os.path.exists(folder):
            continue
            
        print(f"Cleaning: {folder}")
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    size = os.path.getsize(file_path)
                    os.unlink(file_path)
                    deleted_count += 1
                    bytes_freed += size
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    deleted_count += 1
            except Exception as e:
                # Often files are in use, so skip silently or log
                pass

    mb_freed = round(bytes_freed / (1024 * 1024), 2)
    return f"Cleanup complete. Deleted {deleted_count} items. Freed {mb_freed} MB."

def find_files(query, search_path=None):
    """
    Search for files matching a query in the specified path (recursive).
    """
    if not search_path:
        search_path = os.path.join(os.environ['USERPROFILE'], 'Documents') # Default
        
    results = []
    try:
        # Simple glob search - can be improved with regex
        search_pattern = os.path.join(search_path, "**", f"*{query}*")
        
        # Use glob.iglob for iterator to handle large dirs better
        files = glob.glob(search_pattern, recursive=True)
        
        # Limit results
        results = files[:10]
        
        if not results:
            return "No matching files found."
            
        return "\n".join(results)
        
    except Exception as e:
        return f"Error searching files: {str(e)}"

def get_system_stats():
    """
    Get detailed system statistics (CPU, RAM, Disk).
    """
    import psutil
    
    cpu_usage = psutil.cpu_percent(interval=1)
    
    ram_info = psutil.virtual_memory()
    ram_usage = ram_info.percent
    ram_total = round(ram_info.total / (1024**3), 2)
    
    disk_info = psutil.disk_usage('/')
    disk_usage = disk_info.percent
    disk_free = round(disk_info.free / (1024**3), 2)
    
    stats = f"""
    System Status:
    CPU Usage: {cpu_usage}%
    RAM Usage: {ram_usage}% (Total: {ram_total} GB)
    Disk Usage: {disk_usage}% (Free: {disk_free} GB)
    """
    return stats
