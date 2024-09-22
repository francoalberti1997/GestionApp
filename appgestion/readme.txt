EN appgestion/views.py 

tenemos: 
sdk = mercadopago.SDK("APP_USR-5097760030615283-042520-94fa1a3075d7282d39b72833e3961564-1784733023")

donde entre parentesis colocamos el token de la cuenta destinatario.

se nos devuelve un id, que será el preference id.

Después tenemos la APK de Mercado pago en mp/templates/pro-check.html

ahí colocamos el preference id que obtuvimos y el la public key 

public key - Credenciales de la cuenta de MP a vincular
token - Credenciales de la cuenta de MP a vincular

preference_id - de correr appgestion/views.py 
