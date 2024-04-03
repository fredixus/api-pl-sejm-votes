# pl-gov-votes
API do pobierania danych o głosowaniach w sejmie to narzędzie które umożliwia dostęp do danych publicznych z sejmowych obrad a dokładniej głosowań.
Dane dostępne są pod adresem [sejm.gov.pl](http://www.sejm.gov.pl/Sejm9.nsf/agent.xsp?symbol=posglos&NrKadencji=9')

## Opis API
API obejmuje wszystkie głosowania w Sejmie, umożliwiając użytkownikom przeglądanie, wyszukiwanie i analizowanie danych z obrad parlamentu. Możesz przeszukiwać poszczególne głosowania, posłów i ich głosy, a nawet specyficzne projekty ustaw. API jest środowiskiem RESTful, co oznacza, że korzysta z zapytań HTTP do manipulowania i pobierania danych. Odpowiedzi są dostarczane w formacie JSON, który jest łatwo przyswajalny dla większości języków programowania i narzędzi.

## Dokumentacja API
[Dokumentacja API](https://michaldebosz.shinyapps.io/SejmUAT/) 
[![Deploy Shiny App](https://github.com/fredixus/R-SEJM-API-WEB-PAGE/actions/workflows/manual.yml/badge.svg)](https://github.com/fredixus/R-SEJM-API-WEB-PAGE/actions/workflows/manual.yml)

## Szybki przewodnik

### Główne parametry:
- API_URL: [https://w00p2q2p98.execute-api.eu-west-1.amazonaws.com/default/pl-gov/](https://w00p2q2p98.execute-api.eu-west-1.amazonaws.com/default/pl-gov/)
- API_KEY: Skontaktuj się w celu wygenerowania.

### Metody

W celu komunikacji z API należy użyć metody GET.
- Wyświetlenie listy plików [/list/{path+}](https://w00p2q2p98.execute-api.eu-west-1.amazonaws.com/default/pl-gov/list)
- Wyświetlenie listy plików w folderze [/list{path+}](https://w00p2q2p98.execute-api.eu-west-1.amazonaws.com/default/pl-gov/list/9/2023/08/16)
- Pobieranie pliku z folderu [/{path+}](https://w00p2q2p98.execute-api.eu-west-1.amazonaws.com/default/pl-gov/9/2023/08/16)
  -   body {"file":"filename"}
- Pobieranie plików z folderu [/{path+}](https://w00p2q2p98.execute-api.eu-west-1.amazonaws.com/default/pl-gov/9/2023/08/16)
  -   body {"file":["filename1", "filename2"]}

## Znane błędy
Nie wszytkie metody są obecnie zaimplementowane aktualnie można:
- pobrać plik z folderu /KK/YYYY/MM/DD
- pobrać pliki z folderu /KK/YYYY/MM/DD
- wyświetlić zawartość z folderu /list/KK/YYYY/MM/DD
