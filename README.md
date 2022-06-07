# EcoleDirecte-API

![GitHub](https://img.shields.io/github/license/Y0plait/EcoleDirecte-API?style=flat-square)
![Python version](https://img.shields.io/static/v1?label=Python%20version&message=%3C3.4&color=success)

An API to use [Ecole Directe][Ed] in your python scripts.

#### 📌 *Installation :*

Using pip:
`pip install ed-api`

#### 📌 *Basic usage*

```python
import edapi

student = edapi.api.Eleve()
student.login('username','password')

# Method to retrieve the homeworks for a specific day (date must be formatted as YYYY-MM-DD)
student.get_homework('date')

# Method to retreieve notes for a specific period (3 is the whole year, 0 the 1st trimester ...)
student.get_notes(period)
```

To see all the capabilities please read the [documentation][Docs] ;)

[Ed]: https://www.ecoledirecte.com/ "Ecole Directe"
[Docs]: https://github.com/Y0plait/EcoleDirecte-API/wiki "Documentation"
