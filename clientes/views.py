from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
import json
from django.db.models import ProtectedError
from fpdf import FPDF
from datetime import datetime
import locale
from django.templatetags.static import static
import os
from django.conf import settings

#Models import
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
        empresa = data['empresa']
        data = data['tableData']
        date = get_date()

        if empresa == '':
            empresa = 'Nixel'
        data = filter_data(data)
        pdf = create_pdf(date, data, empresa)


        response = HttpResponse(bytes(pdf.output()), content_type='application/pdf')
        response['Content-Disposition'] = "attachment; filename=myfilename.pdf"
        return response
    




def filter_data(data):
    #with open ("data.json") as file:
    #    data = json.load(file)


    for item in data:
        item["Precio"] = item["Precio"][1:]
        if item["Bonificado"] == True:
            item["Bonificado"] = "Si"
            item["Total"] = 0
        else:
            item["Bonificado"] = "No"
            item["Total"] = int(item["Cantidad"]) * int(item["Precio"])
    return data

def create_pdf(date, data, empresa):
    pdf = FPDF()
    pdf.add_page()
    #Got to use this so i can work on both linux/windows enviroments
    image_path = os.path.join(settings.BASE_DIR, 'clientes', 'static', 'media', 'Pag1.jpeg')
    pdf.image(image_path, "C")
    #-----------------------
    pdf.add_page()
    pdf.set_right_margin(20)
    pdf.set_font("times", "", 12)
    presentacion = "Global GPS es una empresa compuesta por un equipo técnico especializado. Le ofrecemos tecnología para que usted, y su equipo de trabajo, recorran los caminos con la mayor información y seguridad."
    pdf.multi_cell(0,5, presentacion, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("times", "", 10)
    pdf.cell(0,20, date, new_x="LMARGIN", new_y="NEXT", align="R" )
    pdf.set_font(style="B")
    pdf.cell(0,5, F"PROPUESTA COMERCIAL: {empresa}", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("helvetica", "b", 10)
    pdf.set_fill_color(255, 255, 0)
    pdf.set_line_width(0.6)
    pdf.cell(45, 10, "Descripcion", border=1, align="C",fill=True)
    pdf.cell(45, 10, "Cantidad", border=1, align="C",fill=True)
    pdf.cell(45, 10, "Precio U.", border=1, align="C",fill=True)
    pdf.cell(45, 10, "Precio Total", border=1, align="C",fill=True)
    pdf.ln(10)
    #comment otu lcoale
    #locale.setlocale(locale.LC_ALL, 'en_US.utf8') #Configuracion local para formato de moneda
    totalMensual = 0
    totalPagoUnico = 0
    for item in data:
        #print(item)
        if item["Bonificado"] == "Si":
            pdf.set_text_color(81, 166, 135)
        pdf.cell(45, 8, item["Nombre"], border=1, align="C")
        pdf.cell(45, 8, str(item["Cantidad"]), border=1, align="C")
        pdf.cell(45, 8, f"$ {format(float(item['Precio']), ',.2f')}", border=1, align="C")
        pdf.cell(45, 8, f"$ {format(float(item['Total']), ',.2f')}", border=1, align="C")
        pdf.ln(8)
        #sumar totales?
        if item["pagoUnico"] == 'True':
            totalPagoUnico += float(item['Total'])
        else:
            totalMensual += float(item['Total'])
        
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(162, 202, 223)
    pdf.cell(45, 6, "", border="RLT", align="C")
    pdf.cell(90, 6, "TOTAL PRESUPUESTADO MENSUAL", border="RLT", align="C", fill=True)
    pdf.cell(45, 6, f"$ {format(float(totalMensual), ',.2f')}", border="RLT", align="C", fill=True)
    pdf.ln(5)
    pdf.cell(45, 6, "", border="RLB", align="C")
    pdf.cell(90, 6, "TOTAL INSTALACION(PAGO UNICO)", border="RLB", align="C", fill=True)
    pdf.cell(45, 6, f"$ {format(float(totalPagoUnico), ',.2f')}", border="RLB", align="C", fill=True)
    pdf.set_font("times", "", 10)
    pdf.ln(20)
    pdf.cell(31, 6, "Mas informacion en: ")
    pdf.cell(31, 6, "http://www.globalgps.com.ar", link="http://www.globalgps.com.ar")



    #-----------------------
    pdf.add_page()
    image_path = os.path.join(settings.BASE_DIR, 'clientes', 'static', 'media', 'Pag3.jpeg')
    pdf.image(image_path, "C")
    pdf.add_page()
    image_path = os.path.join(settings.BASE_DIR, 'clientes', 'static', 'media', 'Pag4.jpeg')
    pdf.image(image_path, "C")
    pdf.add_page()
    image_path = os.path.join(settings.BASE_DIR, 'clientes', 'static', 'media', 'Pag5.jpeg')
    pdf.image(image_path, "C")
    pdf.add_page()
    image_path = os.path.join(settings.BASE_DIR, 'clientes', 'static', 'media', 'Pag6.jpeg')
    pdf.image(image_path, "C")

    return pdf
    pdf.output("PresupuestoGlobalGps.pdf")

def get_date():
    months = ("Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    days = ("Lunes", "Martes","Miercoles","Jueves","Viernes","Sabado","Domingo")
    today = datetime.today()
    week_day = today.weekday()
    date = today.date()
    year, month, day = str(date).split("-")
    return f"{days[week_day]}, {day} de {months[int(month) - 1]} de {year}"