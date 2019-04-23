=============
Common Issues
=============
This page shows some common issues and how to fix them.

--------------
Error messages
--------------

No connection adapters were found for 'hostname.domain.loc/v1/objects/hosts'
============================================================================
When using katprep along with an Icinga2 instance, you're receiving an error like this::

  ERROR:BasicIcinga2APIClient:No connection adapters were found for 'hostname.domain.loc/v1/objects/hosts'

**Reason:** You forgot to specify a correct Icinga2 URL, protocol and port are missing. Use a value like ``https://hostname.domain.loc:5665``

SSL: CERTIFICATE_VERIFY_FAILED
==============================
When accessing the Foreman/Katello API, the following error is displayed::

  File "/usr/lib/python2.7/site-packages/requests/sessions.py", line 576, in send r = adapter.send(request,
  **kwargs) File "/usr/lib/python2.7/site-packages/requests/adapters.py", line 431, in send raise SSLError(e,
  request=request) requests.exceptions.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
  (_ssl.c:579)
  
**Reason:** Your Foreman/Katello server is using a self-signed certificate, use the ``--insecure`` parameter to ignore this error.
