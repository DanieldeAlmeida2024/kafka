"""CLI: publicar/consumir eventos em um Kafka local."""
import argparse
import json
from mensageria.eventos import TOPICOS_PERMITIDOS, criar_evento
from mensageria.servico import PublicadorEventos, criar_produtor, criar_consumidor

def main():
    parser = argparse.ArgumentParser(description='Laboratório Kafka')
    parser.add_argument('--servidor', default='localhost:9094')
    sub = parser.add_subparsers(dest='comando', required=True)
    pub = sub.add_parser('publicar')
    pub.add_argument('--topico', choices=sorted(TOPICOS_PERMITIDOS), required=True)
    pub.add_argument('--tipo', required=True)
    pub.add_argument('--dados', required=True)
    cons = sub.add_parser('consumir')
    cons.add_argument('--topico', choices=sorted(TOPICOS_PERMITIDOS), required=True)
    cons.add_argument('--grupo', default='laboratorio-python')
    args = parser.parse_args()
    if args.comando == 'publicar':
        try:
            evento = criar_evento(args.topico, args.tipo, json.loads(args.dados))
        except ValueError as erro:
            parser.error(str(erro))
        produtor = criar_produtor(args.servidor)
        try:
            PublicadorEventos(produtor).publicar(evento).get(timeout=10)
        finally:
            produtor.close()
        print(f'Evento publicado: {evento.id}')
    else:
        consumidor = criar_consumidor(args.servidor, args.topico, args.grupo)
        try:
            for mensagem in consumidor:
                print(mensagem.value.decode('utf-8'))
                consumidor.commit()
        except KeyboardInterrupt:
            print('Consumo interrompido.')
        finally:
            consumidor.close()

if __name__ == '__main__':
    main()
