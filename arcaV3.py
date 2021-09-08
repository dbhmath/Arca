# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 02:37:34 2019

@author: dbhmath
"""
import time
import click
import sys
import pandas as pd
import json

from selenium import webdriver


def unanota(calificaciones, driver, i, CX, delay=2.5):

    
    cod = -1
    ncorte = {'C1': 1,  'C2': 2,  'C3': 3}

    try:
        student_text = 'STDNT_GRADE_HDR_EMPLID$'+str(i)
        student_name = 'win0divHCR_PERSON_NM_I_NAME$'+str(i)

        elem = driver.find_element_by_id(student_text)
        codigo = int(elem.text)
        nombre = driver.find_element_by_id(student_name).text
        if codigo in calificaciones[CX]:
            nota = calificaciones[CX][codigo]
            if nota < 0.0 or nota > 5.0:
                nota = ''
        else:
            nota = ''
            print(f"Estudiante {nombre} codigo {codigo} no tiene nota.")

        student_grade = 'DERIVED_LAM_GRADE_'+str(ncorte[CX])+'$'+str(i)
        grade = driver.find_element_by_id(student_grade)

        grade.click()
        grade.clear()
        grade.send_keys(str(nota))

        next_i = i + 1 if i == 0 else i-1
        clicker = driver.find_element_by_id(
            'DERIVED_LAM_GRADE_'+str((ncorte[CX]))+'$'+str(next_i))
        clicker.click()
        time.sleep(delay)
        print(i, codigo, CX, nota, nombre)
        cod = codigo

    except:
        print(f"{i} .......")

    return cod



def main():
    print("\nCargando archivo .csv ...")
    params = json.load(open("params.json", 'r'))
    cortes = {'C1',      'C2',      'C3'}
    ok = False

    df = pd.read_csv(params['archivo']+'.csv',
                     delimiter=params['delimeter'], decimal=params['decimal'])
    if len(df.columns) == 2:
        idtype = df.iloc[:, 0].dtype
        cxtype = df.iloc[:, 1].dtype
        if idtype == 'int64' and cxtype == 'float64':
            if df.columns.values[0] == 'ID':
                corte = df.columns.values[1]
                if corte in cortes:
                    ok = True

                    print("\nArchivo csv correcto\n")
                else:
                    print("\nError csv: Corte no corresponde. Debe ser C1, C2 o C3\n")
            else:
                print("\nError csv: Columna de códigos debe llamarse ID\n")
        else:
            print("\nError csv: Tipos de datos no corresponden\n")
    else:
        print("\nError csv: Archivo debe tener 2 columnas\n")
    print(df.head())

    if ok == False:
        print("\n")
        print(df.info(memory_usage=False))
        input("Presione cualquier tecla para finalizar...")
        sys.exit()

    df.set_index('ID', inplace=True)

    # End verificar csv

    calificaciones = df.to_dict()

    options = webdriver.ChromeOptions()
    lang = '--lang='+params['lang']
    options.add_argument(lang)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome("chromedriver.exe", options=options)
    driver.get("https://arca.ecci.edu.co/")


    print("Escriba su usuario y contraseña en el navegador")
    gradebook = click.confirm('Continuar?', default=True)

    if gradebook:
        print("...")
    else:
        print("Suerte es que le digo... agonía")
        driver.close()
        sys.exit()

    try:
        elem = driver.find_element_by_name('Submit')
        elem.click()
    except:
        print("...")

    menu = ['//*[@id="pthnavbca_PORTAL_ROOT_OBJECT"]', '//*[@id="CO_EMPLOYEE_SELF_SERVICE"]',
            '//*[@id="HC_SS_FACULTY_CTR_GBL"]', '//*[@id="crefli_HC_LAM_CLASS_GRADE_GBL"]']

    print("Buscando Cuaderno Evaluación Clase ...")
    time.sleep(3.5)
    for e in menu:
        try:
            elem = driver.find_element_by_xpath(e)
            elem.click()
            time.sleep(1)
            print(".")
        except:
            print("Error menu")

    gradebook = click.confirm(
        'Debe estar en la página en la que digitan las notas. \n(Cuaderno Evaluación Clase) \nContinuar?', default=True)
    codigos = []
    delay = params['timedelay']
    

    while gradebook:

        try:
            frame = driver.find_element_by_xpath('//*[@id="ptifrmtgtframe"]')
            driver.switch_to.frame(frame)
        except:
            print("Error frame")

        try:
            class_name = driver.find_element_by_xpath(
                '//*[@id="DERIVED_SSR_FC_SSR_CLASSNAME_LONG"]')
            print(class_name.text)
        except:
            print("Error Classname")

        j = 0
        intentos = params['intentos']
        while intentos > 0:
            cod = unanota(calificaciones, driver, j, corte, delay)
            j = j + 1
            if cod == -1:
                intentos = intentos - 1
            else:
                codigos.append(cod)
        print("\nCódigos con nota digitada:\n")
        print(codigos)
        print(f"{len(codigos)} notas digitadas\n")

        print(
            "\nEn el navegador ahora debe guardar e ir a otro Cuaderno Evaluación Clase\n")
        time.sleep(1)
        print(".")
        time.sleep(1)
        print("..")
        time.sleep(1)
        print("...")
        time.sleep(1)
        print("....")
        time.sleep(1)
        print(".....")
        gradebook = click.confirm(
            'Debe estar en otro Cuaderno Evaluación Clase) \nContinuar?', default=True)

    print("Suerte es que le digo... agonía")
    time.sleep(3)
    input("Presione cualquier tecla para finalizar...")
    driver.close()
    

if __name__ == '__main__':
    main()
