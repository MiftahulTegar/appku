import os

def request_list(request, *fields):
    values = []
    for field in fields:
        if field == 'document_src':
            values.append(request.files.getlist(f'{field}[]'))
        else:
            values.append(request.form.getlist(f'{field}[]'))
    if values and len(values) == len(fields):
        results = [{} for _ in range(len(values[0]))]
        for x, i in enumerate(values):
            for _x, _i in enumerate(i):
                if _i == '' and fields[x] == 'document_name':
                    _i = 'Sertifikat'
                results[_x][fields[x]] = _i
        return results
    return None

def is_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ['pdf', 'docx']

def is_allowed_cover(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ['pdf', 'png', 'jpg', 'jpeg']

def pdf_only(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ['pdf']

def images(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ['png', 'jpg', 'jpeg']

def allowed_file_size(file):
    max_size = 15 * 1024 * 1024  # 15 MB
    file.seek(0, os.SEEK_END) 
    file_size = file.tell() 
    file.seek(0) 
    return file_size <= max_size
