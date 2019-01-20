from fishshop import app
from OpenSSL import SSL
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('fish_cert.pem')
context.use_certificate_file('fish_key.pem')

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(ssl_context='adhoc', debug=True) # uses dummy certificate
    # uses openssl certificate
    # app.run(host='127.0.0.1', port='5000', debug=True, ssl_context=context)
