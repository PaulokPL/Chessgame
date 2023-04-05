# Chess Game

Bierkę w szachach można przeciągać w dowolne podświetlone miejsce, są to wszystkie dozwolone ruchy, przeciągnięcie poza dozwolone resetuje pozycję do pozycji startowej.

W zamieszczonym polu do wpisywania należy wpisać notację szachową w postaci długiej notacji szachowej, która jest uznawana przez organizacje międzynarodowe
![336918380_9933133706727653_3503322931619839233_n](https://user-images.githubusercontent.com/84084302/229420080-90031cad-38a8-4b80-82d0-b7a1a363cde4.png)
![image](https://user-images.githubusercontent.com/84084302/229420171-afc7a869-d1d2-4ed7-9a89-9b6d1f15fbe5.png)

Zatwierdzić można przyciskiem confirm lub klikając enter. 

Wszystkie reguły gry zostały zaimplementowane do gry:
- bicie w przelocie
- roszada, włączając w to sprawdzanie, czy król nie jest aktualnie szachowany
- promocja piona — na ostatnim polu pojawi się okno dla piona, możemy wtedy wybrać jedną z czterech dostępnych figur
- sprawdzanie szacha i mata — w przypadku tylko szacha, kwadrat pod królem podświetla się na czerwono, w przypadku mata, prócz koloru, pojawia się komunikat o macie w labelu pomiędzy zegarami

Po prawej stronie znajdują się dwa klikalne zegary ze wskazówkami — minutowa, sekundowa i milisekundowa.

Sumarycznie liczba punktów powinna wynosić 15 punktów — ze względu na wykonanie wszystkich zadań i brak punktów ujemnych — jest dziedziczenie po QGraphicsItem, brak słowa kluczowego global, a pętle, których używam, są potrzebne:
- do sprawdzania możliwych ruchów, pętla się kończy, jeśli wykryje jakiś obiekt na swojej drodze
- do sprawdzenia szacha dla króla
- podświetlenia możliwych ruchów, zmiany kolorów planszy
- dodanie wszystkich elementów na początku do sceny

W folderze znajdują się pliki:
- analog_clock.py zawierający kod do zegara analogowego, sprawdza wykonanie ruchu
- change_color.py — zawiera kod do wyświetlenia wiadomości, gdy klikniemy PPM na scenę
- promotion_dialog.py — kod do wyświetlenia okna dialogowego, jeśli pion znajdzie się na ostatnim wierszu
- chess_board.py — dziedziczy po QGraphicsScene, jest to kod dla całej sceny, do której dodajemy elementy, funkcje: update zegara, poruszanie się bierek notacją szachową
- chess_square.py — klasa każdego kwadratu znajdującego się na scenie
- piece.py — klasa pionków — funkcje odpowiadające za klikanie i przeciąganie bierek, aplikacja ruchów (application_movement) - sprawdza możliwość roszady i przesuwa wieżę również, do pionka dopisuje możliwość bicia w przelocie, pop-up — zmienia typ bierki i jego grafikę, get_possible_moves - sprawdza możliwe ruchy dla danego typu pionka, moves_continue sprawdza, czy król nie jest szachowany albo nie będzie w przyszłym ruchu, is_in_check sprawdza dla wszystkich pionków czy jest szach (może mniej, jeżeli już wykrył), is_castling_allowed - sprawdzenie roszady, is_square_occupied - zależało mi, żeby sprawdzić, czy na danym polu jest jakiś pionek, zwrócić ewentualnie jego typ lub kolor 
