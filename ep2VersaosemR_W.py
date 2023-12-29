import threading
import random
import time


class BaseDeDados:
    def __init__(self, palavras):
        self.palavras = palavras
        self.mutex = threading.Lock()

    def ler(self, indice):
        with self.mutex:
            if not self.palavras:
                return None
            palavra = self.palavras[indice]
            return palavra

    def modificar(self, indice):
        with self.mutex:
            if not self.palavras:
                return
            self.palavras[indice] = "MODIFICADO"


class AcessoBase(threading.Thread):
    def __init__(self, nome, base_dados, tipo):
        super().__init__()
        self.nome = nome
        self.base_dados = base_dados
        self.tipo = tipo  # 'leitor' ou 'escritor'
        self.contador = 0  # Adiciona um contador para cada leitor

    def run(self):
        while self.contador < 100:  # Continua até que o contador atinja 100
            indice = random.randint(0, len(self.base_dados.palavras) - 1)

            if self.tipo == 'leitor':
                palavra = self.base_dados.ler(indice)
                if palavra:
                    print(f"{self.nome} leu a palavra: {palavra}")
                    self.contador += 1  # Incrementa o contador
                else:
                    print(f"{self.nome} tentou ler uma palavra, mas todas as palavras já foram lidas.")
                time.sleep(0.001)  # Simula validação
            elif self.tipo == 'escritor':
                self.base_dados.modificar(indice)
                print(f"{self.nome} modificou uma palavra na base.")
                self.contador += 1  # Incrementa o contador

            if self.contador == 100:  # Se o contador atingir 100
                print(f"{self.nome} fez 100 acessos e agora está liberado.")
                time.sleep(0.001)  # Simula validação


            


def criar_arranjo_threads(palavras, num_leitores, num_escritores):
    base_dados = BaseDeDados(palavras)
    leitores = [AcessoBase(f"Leitor-{_ + 1}", base_dados, 'leitor') for _ in range(num_leitores)]
    escritores = [AcessoBase(f"Escritor-{_ + 1}", base_dados, 'escritor') for _ in range(num_escritores)]

    threads = leitores + escritores
    random.shuffle(threads)
    return threads


def executar_sistema(palavras, num_leitores, num_escritores, num_rodadas):
        
    
    tempos = []

    for _ in range(num_rodadas):
        threads = criar_arranjo_threads(palavras, num_leitores, num_escritores)

        tempo_inicial = time.time()

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        tempo_final = time.time()
        tempo_total = tempo_final - tempo_inicial
        tempos.append(tempo_total)

    tempo_medio = sum(tempos) / num_rodadas
    print(f"Tempo médio para {num_leitores} leitores e {num_escritores} escritores: {tempo_medio:.7f} segundos")

   
    return tempo_medio

if __name__ == "__main__":
    palavras = []  # Lista para armazenar as palavras

    with open("D:\\Python Cod\\bd.txt", "r") as arquivo:
        palavras = arquivo.read().splitlines()

    num_rodadas = 50  # Você pode ajustar conforme necessário

    # Abra o arquivo em modo de gravação
    with open('tempos.txt', 'w') as f:
        # Loop de 100 leitores e 0 escritores para 0 leitores e 100 escritores
         for i in range(101):
            num_leitores = 100 - i
            num_escritores = i

            tempo_medio = executar_sistema(palavras, num_leitores, num_escritores, num_rodadas)
            print(f"Versão com SEM Leitores e Escritores Tempo medio para {num_leitores} leitores e {num_escritores} escritores: {tempo_medio} segundos")

            # Escreva o tempo médio no arquivo
            f.write(f"{num_leitores} leitores, {num_escritores} escritores, tempo medio: {tempo_medio} segundos\n")

