from .models import LibraryInfo

def library_settings(request):
    # Берем самую первую (и единственную) запись из настроек
    return {'lib_info': LibraryInfo.objects.first()}