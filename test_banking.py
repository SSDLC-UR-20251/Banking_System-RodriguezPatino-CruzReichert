from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
driver = webdriver.Chrome()
driver.get("http://localhost:5000/login")

# Iniciar sesión
driver.find_element(By.ID, "email").send_keys("sara.palacios@urosario.edu.co")
driver.find_element(By.ID, "password").send_keys("Aa1$aaaa")
driver.find_element(By.ID, "login").click()

time.sleep(2)
#Hacer und deposito
saldo_texto = driver.find_element(By.ID, "saldo_usuario").text
saldo_inicial = float(saldo_texto.split(":")[-1].strip())

driver.find_element(By.ID, "depositar_boton").click()

time.sleep(2)

driver.find_element(By.ID, "balance").send_keys("200")
driver.find_element(By.ID, "depositar").click()

time.sleep(2)

saldo_texto = driver.find_element(By.ID, "saldo_usuario").text
saldo_nuevo = float(saldo_texto.split(":")[-1].strip())

assert(saldo_nuevo == saldo_inicial+200)

#Vamos a validar el retiro de dinero(Flujo feliz)
saldo_texto = driver.find_element(By.ID, "saldo_usuario").text
saldo_inicial = float(saldo_texto.split(":")[-1].strip())

driver.find_element(By.ID, "retirar_boton").click()
time.sleep(2)
driver.find_element(By.ID, "balance").send_keys("200")
driver.find_element(By.ID, "password").send_keys("Aa1$aaaa")
driver.find_element(By.ID, "retirar").click()
time.sleep(2)

saldo_texto = driver.find_element(By.ID, "saldo_usuario").text
saldo_nuevo = float(saldo_texto.split(":")[-1].strip())

assert(saldo_nuevo == saldo_inicial-200)

#Validar que si al retirar se pone mal la clave no se efectue el retiro(Flujo triste):(
saldo_texto = driver.find_element(By.ID, "saldo_usuario").text
saldo_inicial = float(saldo_texto.split(":")[-1].strip())

driver.find_element(By.ID, "retirar_boton").click()
time.sleep(2)
driver.find_element(By.ID, "balance").send_keys("200")
driver.find_element(By.ID, "password").send_keys("Aa1$aa") #Contraseña incorrecta
driver.find_element(By.ID, "retirar").click()
time.sleep(2)

saldo_texto = driver.find_element(By.ID, "saldo_usuario").text
saldo_nuevo = float(saldo_texto.split(":")[-1].strip())
alerta = driver.find_element(By.ID, "alerta_pag_principal").text

assert(alerta == "Tu contraseña es incorrecta =(")
assert(saldo_nuevo == saldo_inicial)

time.sleep(2)
