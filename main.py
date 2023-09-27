# Michael Kemp 22010820
import os
import socket
import _thread
import json
import requests
import urllib.parse
import sys


def extract_http_cmd_URI_Ver(request):
    """Extract command GET, and URI from HTTP request"""
    # \r\n indicates an entire newline of HTTP Request Packet.
    # Using split, we use that as a delimiter, to split each line
    # of HTTP request packet into a list.
    # 1st entry of list is 1st line of HTTP req.
    command_URI_Ver = request.decode().split("\r\n")[0]
    # Break it up into 3 variables  and return
    command, URI, Ver = command_URI_Ver.split()

    return command, URI, Ver


def read_file(filename, binary=False):
    """Read file in could be binary, shown this code in class"""
    if binary:
        mode = 'rb'
    else:
        mode = 'r'
    with open(filename, mode) as fin:
        content = fin.read()
    return content


def parse_post(payload):
    """Parse POST request payload, by turning into dict and then
    writing to answers.JSON file"""
    answers_dict = {}

    items = payload[0].split("&")
    # print("ITEMS ARE" + str(items))
    # print("*" * 30)
    psych_q_list = []
    pet_list = []
    for item in items:
        key, val = item.split("=")
        # Parse spaces from + to " "
        val = val.replace("+", "")
        answers_dict[key] = val

        # If data received is psychological question. extract from payload turn to list
        if key[:8] == "question":
            answers_dict.pop(key)
            psych_q_list.append(int(val))
        if key[:4] == "pets":
            answers_dict.pop(key)
            pet_list.append(val)
        if key[:7] == "message":
            # Parse message from uRL format - quic hack around.
            decoded_message = urllib.parse.unquote(val)
            answers_dict.pop(key)
            answers_dict[key] = decoded_message

    # append psychological question list to new dictionary
    answers_dict["questions"] = psych_q_list

    # append pet list to new dictionary
    answers_dict["pets"] = pet_list

    # Get rid of submit from answers_dict
    answers_dict.pop("submit")

    # Answers dictionary can be converted to JSON to be saved as file.
    # So that JavaScript can AJAX request it.
    answers_dict_json = json.dumps(answers_dict)
    answers_file = open("answers.json", "w")
    answers_file.write(answers_dict_json)
    answers_file.close()


def get_proper_job_name(answer_data):
    """Give proper job name from deserialized data.
    # Also add movieURI # Using IMDB ID and my API key"""
    chosen_job = ""
    if answer_data["job"] == "ceo":
        chosen_job = "CEO of large mega-corporation"
        # Steve Jobs movie for CEO
        movie_uri = "https://www.omdbapi.com/?apikey=b5d57bd0&i=tt2080374"
    elif answer_data["job"] == "astronaut":
        chosen_job = "Astronaut"
        # Interstellar for Astronaut
        movie_uri = "https://www.omdbapi.com/?apikey=b5d57bd0&i=tt0816692"
    elif answer_data["job"] == "doctor":
        chosen_job = "Medical doctor"
        # Concussion 2015 for Medical Doctor
        movie_uri = "https://www.omdbapi.com/?apikey=b5d57bd0&i=tt3322364"
    elif answer_data["job"] == "model":
        chosen_job = "Fashion model"
        # The devil wears prada for Fashion Model
        movie_uri = "https://www.omdbapi.com/?apikey=b5d57bd0&i=tt0458352"
    elif answer_data["job"] == "rockstar":
        chosen_job = "Rock star"
        # Elvis Movie for Rock Star
        movie_uri = "https://www.omdbapi.com/?apikey=b5d57bd0&i=tt3704428"
    elif answer_data["job"] == "garbage":
        chosen_job = "Refuse collection operative"
        # WALL-E for Refuse collection operative
        movie_uri = "https://www.omdbapi.com/?apikey=b5d57bd0&i=tt0910970"
    return chosen_job, movie_uri


def generate_most_suited_job(answer_data):
    """Generate most suited job based on answers to questions.
    Hardcode answers that suit each profession.
    Calculate which most suited profession user's answer is closest to for each question
    Increase count in dictionary for which profession(s) are most suited.
    Highest count(s) of most suited jobs for all questions is the pick."""

    hardcoded_scores = {
        "CEO of large mega-corporation": [3, 4, 5, 4, 2, 4, 5, 4, 2, 5, 4, 2, 3, 3, 2, 3, 2, 2, 3, 4],
        "Astronaut": [3, 5, 4, 5, 1, 5, 4, 3, 1, 5, 4, 1, 2, 5, 1, 4, 2, 2, 1, 5],
        "Medical doctor": [5, 4, 4, 5, 1, 5, 5, 3, 4, 5, 5, 2, 5, 1, 1, 3, 2, 3, 4, 4],
        "Fashion model": [4, 1, 1, 1, 5, 2, 1, 5, 5, 1, 1, 5, 2, 3, 3, 1, 4, 4, 1, 1],
        "Rock star": [5, 3, 5, 1, 5, 2, 3, 5, 5, 1, 3, 5, 4, 1, 4, 1, 5, 5, 1, 1],
        "Refuse collection operative": [1, 2, 1, 3, 5, 1, 1, 2, 5, 3, 1, 5, 1, 5, 5, 5, 4, 1, 3, 3]
    }

    most_suited_tally = {}
    most_suited_jobs = []
    # Create the most suited job overall for every question.
    for i in range(len(answer_data["questions"])):
        # Loop for each question
        current_question_diffs = {}
        # print("*******")
        counter = 0
        for key, value in hardcoded_scores.items():
            # Get difference between user answers and hardcoded for each job for each question
            diff = abs(value[i] - answer_data["questions"][i])
            current_question_diffs[key] = diff
            counter += 1
            if counter == 6:
                # Once all differences for each occupation added to current_question_diffs, find most suited jobs = those with smallest difference, can be multiple.
                # print(current_question_diffs)
                minval = min(current_question_diffs.values())
                # print({k: v for k, v in current_question_diffs.items() if v == minval})

                # add count of these minimum keys to total tally.
                for job, difference in current_question_diffs.items():
                    if difference == minval:
                        if job not in most_suited_tally:
                            most_suited_tally[job] = 1
                        else:
                            most_suited_tally[job] += 1

    # Loop through tally and add most suited job or jobs to the tally.
    # print("MOST SUITED TALLY:")
    # print(most_suited_tally)
    highest_tally = max(most_suited_tally.values())

    for k, v in most_suited_tally.items():
        if v == highest_tally:
            most_suited_jobs.append(k)
    # print(most_suited_jobs)

    return most_suited_jobs


def create_folder(folder_name):
    """Utility to create new folder"""
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)


def write_animal_img(pet_img_url, pet):
    """Write animal images to correct files.
    Return file name of the pet"""
    curld_img = requests.get(pet_img_url)
    pet_file_name = "images/" + pet + "s/" + os.path.basename(pet_img_url)

    with open(pet_file_name, "wb") as fout:
        fout.write(curld_img.content)
        fout.close()
    return pet_file_name


def generate_pet_images(answer_data, pet_img_dict):
    """Create folders if they don't already exist
    Pull images from APIS for each animal selected
    save the files on server
    Update pet image dictionary, which will be used psych profile json.
    """
    # Create directory system for animal pictures.
    create_folder("images")
    create_folder("images/dogs")
    create_folder("images/cats")
    create_folder("images/ducks")

    for pet in answer_data["pets"]:
        if pet == "dog":
            pet_uri = "https://dog.ceo/api/breeds/image/random"
            pet_response = requests.get(pet_uri)
            output = pet_response.json()
            pet_img_url = output["message"]

            # Only saving jpegs.
            if pet_img_url[-3:] != "jpg":
                # Recurse until we get a jpeg returned.
                generate_pet_images(answer_data, pet_img_dict)
            else:
                dog_file_name = write_animal_img(pet_img_url, pet)
                pet_img_dict[pet] = dog_file_name

        elif pet == "cat":
            pet_uri = "https://api.thecatapi.com/v1/images/search"
            pet_response = requests.get(pet_uri)
            output = pet_response.json()
            json_out = output[0]
            pet_img_url = json_out["url"]

            # Only saving jpegs.
            if pet_img_url[-3:] != "jpg":
                generate_pet_images(answer_data, pet_img_dict)
            else:
                cat_file_name = write_animal_img(pet_img_url, pet)
                pet_img_dict[pet] = cat_file_name

        elif pet == "duck":
            pet_uri = "https://random-d.uk/api/v2/random"
            pet_response = requests.get(pet_uri)
            output = pet_response.json()
            pet_img_url = output["url"]

            # Only saving jpegs.
            if pet_img_url[-3:] != "jpg":
                generate_pet_images(answer_data, pet_img_dict)
            else:
                duck_file_name = write_animal_img(pet_img_url, pet)
                pet_img_dict[pet] = duck_file_name


def generate_psych_profile():
    """
    Create new JSON File that contains:
        user details
        preferred job
        message
        Actual recommended job
        Recommendation from movies
        pet images
    """
    psychological_profile_dict = {}
    # load in the answers.json
    answers = read_file("answers.json")
    answer_data = json.loads(answers)  # deserialize the JSON.

    # Add in user details
    psychological_profile_dict = answer_data.copy()
    psychological_profile_dict.pop("questions")
    psychological_profile_dict.pop("pets")
    psychological_profile_dict.pop("job")

    # Find most suited jobs.
    most_suited_jobs = generate_most_suited_job(answer_data)
    chosen_job, movie_uri = get_proper_job_name(answer_data)
    print("JOBS:")
    print(chosen_job)
    print(most_suited_jobs)

    # Add in most suited jobs and full chosen job name.
    psychological_profile_dict["chosen_job"] = chosen_job
    psychological_profile_dict["most_suited_jobs"] = most_suited_jobs

    # MOVIE OMDB Here is your key: b5d57bd0
    # Wanted to do it via genres but API uses title or IMDB ID.
    movie_response = requests.get(movie_uri)
    # Add movie to psych profile
    psychological_profile_dict["movie"] = movie_response.json()

    # PET IMAGES:
    pet_img_dict = {}
    generate_pet_images(answer_data, pet_img_dict)
    # add pets and images to psych profile.
    psychological_profile_dict["pets"] = pet_img_dict

    print("NEW PSYCHOLOGICAL PROFILE: " + str(psychological_profile_dict))

    # Save psychological profile as JSON.
    psychological_profile_dict_json = json.dumps(psychological_profile_dict)
    psych_file = open("psychprofile.json", "w")
    psych_file.write(psychological_profile_dict_json)
    psych_file.close()


def basic_auth(connectionSocket, request):
    """Authentication for HTTP server"""
    headers = request.decode()
    headers_dict = {}
    headers = request.decode().split("\r\n")
    # Put all header lines into dictionary, minus 2 blank lines at end.
    for i in range(1, len(headers) - 2):
        key, val = headers[i].split(": ")
        headers_dict[key] = val

    if "Authorization" in headers_dict:
        if headers_dict["Authorization"][6:] == "MjIwMTA4MjA6MjIwMTA4MjA=":
            return True
        else:
            return False


def http_response(connectionSocket):
    # Receive data (at most 10240 bytes)
    request = connectionSocket.recv(10240)

    # Exceptions have been thrown when browser exits page.
    if not request:
        print("Empty request received")
        return

    command, URI, HTTPVer = extract_http_cmd_URI_Ver(request)

    if URI == "/":
        URI = "index.html"
    if URI == "/form":
        URI = "psycho.html"
    if URI == "/view/input":
        URI = "answers.json"
    if URI == "/view/profile":
        URI = "psychprofile.json"

    # Read files in, no matter the type, getting rid of front/ and rear /
    # jpg has rear /
    filename = URI.strip("/")  # page.html

    # if no file extension don't add one.
    if len(filename.split('.')) == 1:
        print("page requested no extension, probably a POST")
    else:
        filetype = filename.split('.')[1]  # html / .jpg

    # Authenticate the user
    if not basic_auth(connectionSocket, request):
        response = 'HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm="Web 159352"\r\nContent-Type: ' \
                   'text/plain\r\nContent-Length: 0\r\n\r\n'
        connectionSocket.sendall(response.encode())
        connectionSocket.close()
        return

    # Handle the analysis action for the psycho.html form.
    if command == 'POST' and URI == '/analysis':
        print("Got a form Post Request.")
        payload = request.decode().split("\r\n\r\n")[-1:]

        if payload == ['']:
            # Some browser are sending this if connection closed.
            print("EMPTY PAYLOAD")
            connectionSocket.close()
        else:
            parse_post(payload)
            generate_psych_profile()
            # send nice message:
            response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 1048\r\n\r\n' \
                       '<html><body><p>Thankyou</p></body></html>\r\n'
            connectionSocket.sendall(response.encode())

    else:
        if os.path.exists(filename):
            if filetype == "html":
                # Read content in from file
                content = read_file(filename)
                # Send the HTTP response back to the client 200 if authenticated, 401 if not.
                response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + content
                connectionSocket.sendall(response.encode())
            elif filetype == "css":
                # Read content in from file
                content = read_file(filename)
                # Send the HTTP response back to the client 200 if authenticated, 401 if not.
                response = 'HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\n' + content
                connectionSocket.sendall(response.encode())
            elif filetype == "jpg":
                # If .jpg from GET exists in local dir and has extension .jpg  serve it
                content = read_file(filename, binary=True)
                jpg_response = 'HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n\r\n'
                connectionSocket.sendall(jpg_response.encode())
                connectionSocket.send(content)
            elif filetype == "json":
                content = read_file(filename)
                # Send the HTTP response back to the client 200 if authenticated, 401 if not.
                response = 'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n' + content
                connectionSocket.sendall(response.encode())
        else:
            # If file doesn't exist in local dir
            # Send the HTTP response back to the client
            response2 = 'HTTP/1.1 404 Not found\r\nContent-Type: text/html\r\n\r\n'
            connectionSocket.sendall(response2.encode())
    connectionSocket.close()



def start_server(server_port):
    """For Docker we need the port as a command line argument."""
    # Create socket instance internet socket + TCP:
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind socket to host and port blank is localhost
    mySocket.bind(('', server_port))

    # Accept connections:
    mySocket.listen()
    # Server will wait for client to connect.
    while True:
        # Accept connection
        connectionSocket, addr = mySocket.accept()
        # After listening and connection accepted start thread
        # start_new_thread, function is first arg. then tuple of arguments
        # sent to client_connection_thread
        _thread.start_new_thread(http_response, (connectionSocket,))



if __name__ == '__main__':
    if len(sys.argv) > 1:
        serverPort = int(sys.argv[1])
    else:
        serverPort = 8080

    start_server(serverPort)

