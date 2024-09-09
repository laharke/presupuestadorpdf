from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
import json
from django.db.models import ProtectedError
from fpdf import FPDF




from .models import User, Dispositivo

# Create your views here.

def index(request):
    return render(request, "index.html")

def login_view(request):
    # Si es GET rendereo el login.html si es POST chequeo loggin credentials y redercciono al index.
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        print(username, password)
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {
                "alert": "error",
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def abm_dispositivos(request):
    if request.method == "POST":
        pagoUnico = True if "pagoUnico" in request.POST else False
        dispositivo = Dispositivo(
                nombre = request.POST["nombreDispositivo"],
                precio = request.POST["precioDispositivo"],
                pagoUnico = pagoUnico
            )
        dispositivo.save()
    #Siempre cargo la tabla con dispositvos
    dispositivos = Dispositivo.objects.all()
    
    return render(request, "abm_dispositivos.html", {
        "dispositivos": dispositivos
    })

def borrar_dispositivo(request):
    #Parseo la data del body que viene en el post.
    data = request.body
    data = data.decode('utf-8')
    data = json.loads(data)
    
    instance = Dispositivo.objects.get(id = data['id'])
    try:
        instance.delete()
        return JsonResponse({'result':'ok'})
    except ProtectedError:
        return JsonResponse({'result':'error'})
    
def edit_dispositivos(request):
    
    #Buscar el objeto que tengo que editar
    dispositivo = Dispositivo.objects.get(pk = request.POST["idEdicion"])
    pagoUnico = True if "pagoUnicoEdicion" in request.POST else False


    dispositivo.nombre = request.POST["nameEdicion"]
    dispositivo.precio = request.POST["precioEdicion"]
    dispositivo.pagoUnico = pagoUnico
    dispositivo.save()
        
    #Siempre cargo la tabla con dispositvos
    dispositivos = Dispositivo.objects.all()

    return HttpResponseRedirect(reverse("abm_dispositivos"))

#Generar PDf view, si es un get va a traer toda la ifno de dispositovs ya rmar una TABLA
#Si es un post llama al afuncoi nde generar y guardar  PDF??
def generar_pdf(request):
    if request.method == "GET":
        dispositivos = Dispositivo.objects.all()
        return render(request, "generar_pdf.html", {
            "dispositivos": dispositivos
         })
    else:
        #Generar PDF, si es POST viene con toda la info
        data = request.body
        data = data.decode('utf-8')
        data = json.loads(data)
        #print(data)
        for dict in data:
            print(dict)
            print(type(dict))

        # Create instance of FPDF class
        pdf = FPDF()
        pdf.add_page()

        # Set title and fonts
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(40, 10, 'Hello from Django!', ln=True)
        
        # Add a line of text
        pdf.set_font('Arial', '', 12)
        pdf.cell(40, 10, 'This is a sample PDF created with FPDF in Django.', ln=True)

        response = HttpResponse(bytes(pdf.output()), content_type='application/pdf')
        response['Content-Disposition'] = "attachment; filename=myfilename.pdf"
        return response

        return JsonResponse({'result':'ok'})