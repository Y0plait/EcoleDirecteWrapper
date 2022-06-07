import requests
import json
from base64 import b64decode

import EcoleDirecteWrapper.exceptions as ApiExceptions


class EcoleDirecteAPIObject(object):

    def __init__(self, base_url):
        self.url = base_url

    def _get(self, endpoint, **kwargs):
        """
        Method to perform get requests on the API.

        :param endpoint: endpoint of the API.

        :return: response of the GET request.
        """
        return self._request(endpoint, 'get', **kwargs)

    def _post(self, endpoint, data, **kwargs):
        """
        Method to perform POST requests on the API.

        :param endpoint: endpoint of the API.
        :param data: data of the POST request.

        :return: response of the POST request.
        """
        return self._request(endpoint, 'post', data, **kwargs)

    def _request(self, endpoint, method, data=None, **kwargs):
        """
        Method to handle both GET and POST requests.

        :param endpoint: endpoint of the API.
        :param method: method of HTTP request (GET or POST).
        :param data: POST data for the request.

        :return: response of the request.
        """
        final_url = self.url + endpoint

        if not self._is_authenticated:
            raise ApiExceptions.LoginRequired('Please login first.')

        if method == 'get':
            request = self.session.get(final_url, **kwargs)
        else:
            request = self.session.post(final_url, data, **kwargs)

        # Raise exception if request return HTTP error
        request.raise_for_status()
        request.encoding = 'utf_8'

        # If request result length equals to 0 (GET request) then:
        if len(request.text) == 0:
            data = json.loads('{}')
        else:
            try:
                data = json.loads(request.text)
            except ValueError:
                data = request.text

        return data

    def login(self, username, password, account_number=0):
        """
        Method to authenticate the API.
        Setup a session that 'll be used all the long.

        :param username: username.
        :param password: password.

        :return: response to login request.
        """
        post_data = f'data={{"uuid": "","identifiant": "{username}","motdepasse": "{password}","isReLogin": "false"}}'

        self.session = requests.Session()
        login = self.session.post('https://api.ecoledirecte.com/v3/login.awp',
                                  post_data)

        login_data = json.loads(login.text)
        if login_data['code'] == 200:
            self._is_authenticated = True
            # TODO reformat url with student id
            self.id = str(login_data['data']['accounts'][account_number]['id'])
            self._user_data = login_data['data']
            self.token = login_data['token']
            self.x_token = login.headers['X-Token']

        elif login_data['code'] == 505:
            raise ApiExceptions.InvalidLogin(
                f'Invalid Credentials.Please check your credentials and retry.\n\
                 Server response: {login_data}')

        else:
            raise ApiExceptions.ServerError(
                f'An unknown error occured.\n\
                  Server response: {login_data}'
            )


class Eleve(EcoleDirecteAPIObject):

    def __init__(self):
        """
        Initialize the class.
        """

        super(EcoleDirecteAPIObject).__init__()

        # Base url
        self.url = 'https://api.ecoledirecte.com/v3/'

        # User is by default not logged in so not authenticated
        self._is_authenticated = False

    def retrieve_notes(self):
        """
        Retrieve raw grades of all the year from the API 

        :return: raw json dict from the request.
        """

        return self._post(f'eleves/{self.id}/notes.awp?verbe=get', 'data={}', headers={"X-Token": self.x_token})['data']

    def get_notes(self, period=3):
        """
        Method to format notes by using the retrieve_notes method.

        :param period: period of the year (integer) -> 0: 1st trimester, 1: 2nd trimester,
        2: 3rd trimester, 3: whole year

        :return: dict with notes sorted by periode, subjects and with their name.
        """

        if not period <= 0 and period >= 3:
            raise ApiExceptions.UnexistantPeriod(
                "Please specify an integer between 0 and 3 included.")

        notes_data = self.retrieve_notes()
        idPeriode = notes_data['periodes'][period]['idPeriode']

        # Extracting generic data:
        fperiod = {
            "period_name": notes_data['periodes'][period]['periode'],
            "principalProfessorName": notes_data['periodes'][period]['ensembleMatieres']['nomPP'],


            "startDate": notes_data['periodes'][period]['dateDebut'],
            "endDate": notes_data['periodes'][period]['dateFin'],
            "is_finished": notes_data['periodes'][period]['cloture'],
            "class_council": {
                "date": notes_data['periodes'][period]['dateConseil'],
                "time": notes_data['periodes'][period]['heureConseil'],
                "room": notes_data['periodes'][period]['salleConseil']
            },
            "grades": {
                "overall_avrg": {
                    "student": notes_data['periodes'][period]['ensembleMatieres']['moyenneGenerale'],
                    "class": notes_data['periodes'][period]['ensembleMatieres']['moyenneClasse'],
                    "min_class": notes_data['periodes'][period]['ensembleMatieres']['moyenneMin'],
                    "max_class": notes_data['periodes'][period]['ensembleMatieres']['moyenneMax']
                }
            }
        }

        # Exctracting specific data:
        for matieres in range(0, len(notes_data['periodes'][period]['ensembleMatieres']['disciplines'])):
            fperiod['grades'].update({
                notes_data['periodes'][period]['ensembleMatieres']['disciplines'][matieres]['discipline']: {
                    "professor": notes_data['periodes'][period]['ensembleMatieres']['disciplines'][matieres]['professeurs'],
                    "coef": notes_data['periodes'][period]['ensembleMatieres']['disciplines'][matieres]['coef'],
                    "overall_avrg": {
                        "student": notes_data['periodes'][period]['ensembleMatieres']['disciplines'][matieres]['moyenne'],
                        "class": notes_data['periodes'][period]['ensembleMatieres']['disciplines'][matieres]['moyenneClasse'],
                        "min_class": notes_data['periodes'][period]['ensembleMatieres']['disciplines'][matieres]['moyenneMin'],
                        "max_class": notes_data['periodes'][period]['ensembleMatieres']['disciplines'][matieres]['moyenneMax']
                    },
                    "studentNmbr": notes_data['periodes'][period]['ensembleMatieres']['disciplines'][matieres]['effectif']
                }
            })

        return fperiod

    def get_homework(self, date: str):
        """
        Retrieve raw homeworks at the asked date 

        :param date: date of the asked day. must be in YYYY-MM-DD

        :return: raw json dict from the request.
        """

        return self._post(f'Eleves/{self.id}/cahierdetexte/{date}.awp?verbe=get', 'data={}', headers={"X-Token": self.x_token})['data']

    def ical_url_student(self):
        """
        Return the .ical's file url
        """

        return self._post(f'ical/E/{self.id}/url.awp?verbe=get', 'data={}', headers={"X-Token": self.x_token})['data']['url']

    def ical_url_general(self):
        """
        Return ical's general file url
        """

        return self._post('ical/GEN/0/url.awp?verbe=get', 'data={}', headers={"X-Token": self.x_token})['data']['url']

    @ property
    def api_version(self):
        """
        Get EcoleDirecte API version.

        :return: api version.
        """
        return "v3"

    @ property
    def student_informations(self) -> dict:
        """
        Extract informations about the student

        :return: dict with informations
        """
        if not self._is_authenticated:
            raise ApiExceptions.LoginRequired('Please login first.')

        student_info = {
            'name': self._user_data['accounts'][0]['nom'],
            'surname': self._user_data['accounts'][0]['prenom'],
            'class': self._user_data['accounts'][0]['profile']['classe']['libelle'],
            'email': self._user_data['accounts'][0]['email'],
            'student_id': str(self._user_data['accounts'][0]['id']),
            'school_name': self._user_data['accounts'][0]['nomEtablissement'],
            'last_connexion': self._user_data['accounts'][0]['lastConnexion'],
            'photo_url': self._user_data['accounts'][0]['profile']['photo'],
            'sexe': self._user_data['accounts'][0]['profile']['sexe']
        }

        return student_info


class Parent(EcoleDirecteAPIObject):

    def __init__(self) -> None:
        super(EcoleDirecteAPIObject).__init__()

        # TODO Parent class
        # Base url of the API
        self.url = 'https://api.ecoledirecte.com/v3/2/'

        # User is by default not logged in so not authenticated
        self._is_authenticated = False

    def get_timeline(self):
        """
        Get the timeline of the account
        """

        return self._post('timelineAccueilCommun.awp?verbe=get', 'data={}', headers={"x-token": self.x_token})['data']

    def list_mails(self):
        """
        Fetch the name & id of the mails.

        :return : dict with all the mails
        """
