uripath = "http://www.xyzbooks.co.nz/titles/byauthor?name=Lucinda+Becker"
start_of_name = uripath.find('name=') + len('name=')
name = uripath[start_of_name:]
name = name.split('&')[0]
name = name.replace('+', ' ')

import json
name_dict = {"name": name}
serialised_name_dict = json.dumps(name_dict)

response = f'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(serialised_name_dict)}\r\n\r\n{serialised_name_dict}'

print(name)