import parkeerplaatsen as p
import toegangruimtes as t
import qr as q
import rfid as rf
import multiprocessing
import time
import paho.mqtt.client as mqtt

parkeer = p.Parkeren()
toegang = t.Toegang()
qr_code = q.qr()
rfid = rf.rfid()

def mqtt_setup():
    client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311, transport=”tcp”)
    client= mqtt.Client(client_name)
    connect(host, port=1883, keepalive=60, bind_address="")
    client.connect(host_name)

    return client

def main():
    '''Functie die aangeroepen wordt om de QR
    of RFID code te scannen. Code runt totdat
    een van de 2 gevonden is.
    
    Args:
    None

    Returns:
    ret_value'''

    found_event = multiprocessing.Event()

    ret_value1 = multiprocessing.Value("i", 0)
    ret_value2 = multiprocessing.Value("i", 0)

    p1 = multiprocessing.Process(target=qr_code.scan_qrcode, args=[ret_value1, found_event])
    p1.start()

    p2 = multiprocessing.Process(target=rfid.read_card, args=[ret_value2, found_event])
    p2.start()
   
    found_event.wait()
    p1.terminate()
    p2.terminate()

    return (ret_value1.value + ret_value2.value)




def user_menu(client):
    while True:
        print('Welkom tot het toegangsmenu!\n \n')
        antwoord = str(input('Wilt u parkeren? (ja of nee): '))
        if (antwoord.lower()) == 'ja':
            kant = str(input('Wilt u in op uit de garage? (in of uit) '))
            if kant.lower() == 'in':
                direction = 1
            elif kant.lower() == 'uit':
                direction = 0
            else:
                print('Uw antwoord is niet valide.')
                continue
            print("Scan uw RFID kaart of QR code")
            result = (parkeer.parkeer(main(), direction))
            
            if result[0]:
                client.publish("sensor/green_light","ON")
                print(result[1])
                time.sleep(5)
                client.publish("sensor/green_light","OFF")
                continue
            client.publish("sensor/red_light","ON")
            print(result[1])
            time.sleep(5)
            client.publish("sensor/red_light","OFF")
            continue
            
        elif (antwoord.lower()) != 'nee':
            print('Uw antwoord is niet valide.')
            continue
        print('\n \n')
        antwoord = str(input('Wilt u toegang krijgen tot een ruimte? (ja of nee): '))
        if (antwoord.lower()) == 'ja':
            print("Welke ruimte zou u toegang tot willen? \n")
            lines = 0
            for line in (toegang.get_ruimtes()):
                print('{0} -- Met de naam {1}'.format(line[0], line[1]))
                lines = lines + 1
            ruimte = int(input('Selecteer het nummer: '))
            if ruimte < 1 or ruimte > lines:
                print('Uw antwoord is niet valide.')
                continue
            else:
                result = toegang.vraag_toegang(main(), ruimte)
                if result:
                    client.publish("sensor/green_light","ON")
                    print("U heeft toegang."
                    time.sleep(5)
                    client.publish("sensor/green_light","OFF")
                    continue
                client.publish("sensor/red_light","ON")
                print("U heeft geen toegang"
                time.sleep(5)
                client.publish("sensor/red_light","OFF")
                continue
        elif (antwoord.lower()) != 'nee':
            print('Uw antwoord is niet valide.')
            continue

if __name__ == '__main__':

    client = mqtt_setup()
    user_menu(client)
    