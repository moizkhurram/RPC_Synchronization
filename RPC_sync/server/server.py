from xmlrpc.server import SimpleXMLRPCServer
import os
import threading
current_path = os.getcwd()
current_path = current_path.replace("\\", "/")
UPLOADS_FOLDER = current_path+'/sync_server'
print(UPLOADS_FOLDER)
def upload_file(file_name, file_data):
    with open(os.path.join(UPLOADS_FOLDER, file_name), 'wb') as file:
        file.write(file_data.data)
    return True

def download_file(file_name):
    file_path = os.path.join(UPLOADS_FOLDER, file_name)
    try:
        if not os.path.isfile(file_path):
            return None

        with open(file_path, 'rb') as file:
            file_data = file.read()
    
        return file_data
    except:
        return None

def delete_file(file_name):
    file_path = os.path.join(UPLOADS_FOLDER, file_name)
    if not os.path.isfile(file_path):
        return False
    
    os.remove(file_path)
    return True

def rename_file(old_name, new_name):
    old_path = os.path.join(UPLOADS_FOLDER, old_name)
    new_path = os.path.join(UPLOADS_FOLDER, new_name)
    if not os.path.isfile(old_path):
        return False

    os.rename(old_path, new_path)
    return True

def start_server(port):
    server = SimpleXMLRPCServer(('localhost', port))
    server.register_function(upload_file, 'upload')
    server.register_function(download_file, 'download')
    server.register_function(delete_file, 'delete')
    server.register_function(rename_file, 'rename')

    # Function to handle client requests in a separate thread
    def serve_forever_thread():
        server.serve_forever()

    # Create and start the server thread
    server_thread = threading.Thread(target=serve_forever_thread)
    server_thread.start()

    # Wait for the server thread to finish
    server_thread.join()

start_server(9000)  # Change the port number as desired
