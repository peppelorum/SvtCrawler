SVT Crawler
=============

SVT Crawler är en webspindel som indexerar SVT Play.

V 0.1

Flöde
------------
- Man specar i en textfil vilka textsträngar som ska sökas efter
- Spindeln tröskar igenom SVT Play och matchar strängarna mot titeln på sidan
- Om träff, så läggs URL:en in i databasen
- Sen betar man av posterna en efter en och laddar hem dem

Data
---------
- Alla träffar sparas i en enkel SQLAlchmey-db (sqlite) och ser typ ut som (i djangomodelsyntax då):
    STATES = ((1, 'Träff'), (2, 'Ladda ned'), (3, 'Ladda ej ned')) # Yada, yada
    class Hit():
        url = models.TextField()
        created = models.DateTimeField()
        state = models.IntegerField(choices=STATES)


Frågor
---------
- Vad kan man köra för ratelimit mot svtplay.se?
- Ska man kunna skicka med en callbackfunktion/script som ska köras vid träff, eller ska man låta nedladdaren traggla på för sig själv?

Framtida utveckling
-----------------
- Man skulle kunna tänka sig en enkel frontend som listar alla poster i db:n, sen kan man bara bocka för om man vill att
de ska laddas hem eller ej.