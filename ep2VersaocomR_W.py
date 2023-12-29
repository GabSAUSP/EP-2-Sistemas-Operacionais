import threading
import random
import time

class BaseDeDados:
    def __init__(self, palavras):
        self.palavras = palavras
        self.mutex = threading.Lock()

    def acessar(self, indice):
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

class LeitorEscritorThread(threading.Thread):
    def __init__(self, nome, base_dados, semaforo_leitura, semaforo_escrita, leitores, escritores):
        super().__init__()
        self.nome = nome
        self.base_dados = base_dados
        self.semaforo_leitura = semaforo_leitura
        self.semaforo_escrita = semaforo_escrita
        self.leitores = leitores
        self.escritores = escritores

    def leitor_entra(self):
        with self.semaforo_leitura:
            self.leitores[0] += 1
            if self.leitores[0] == 1:
                self.semaforo_escrita.acquire()

    def leitor_sai(self):
        with self.semaforo_leitura:
            self.leitores[0] -= 1
            if self.leitores[0] == 0:
                self.semaforo_escrita.release()

    def run(self):
        with self.escritores:  # Entra na região crítica
            for _ in range(100):
                self.leitor_entra()

                if not self.base_dados.palavras:
                    print(f"{self.nome} terminou de ler todas as palavras.")
                    break

                indice = random.randint(0, len(self.base_dados.palavras) - 1)
                palavra = self.base_dados.acessar(indice)

                if palavra:
                    print(f"{self.nome} leu a palavra: {palavra}")
                else:
                    print(f"{self.nome} terminou de ler todas as palavras.")

                self.leitor_sai()

            # Sai da região crítica após o 100º acesso
            if self.leitores[0] == 0:
                self.semaforo_escrita.release()

        # Simula a validação após ler todas as palavras
        time.sleep(0.001)

class Escritor(LeitorEscritorThread):
    def __init__(self, nome, base_dados, semaforo_leitura, semaforo_escrita, leitores, escritores, condicao):
        super().__init__(nome, base_dados, semaforo_leitura, semaforo_escrita, leitores, escritores)
        self.condicao = condicao

    def run(self):
        with self.escritores:  # Entra na região crítica
            for _ in range(100):
                with self.condicao:
                    while self.leitores[0] > 0:
                        self.condicao.wait()

                with self.semaforo_escrita:
                    if not self.base_dados.palavras:
                        print(f"{self.nome} terminou de modificar todas as palavras.")
                        break

                    indice = random.randint(0, len(self.base_dados.palavras) - 1)
                    self.base_dados.modificar(indice)
                    print(f"{self.nome} modificou uma palavra na base.")

            

                # Sai da região crítica após a validação
                self.semaforo_escrita.release()
            # Simula a validação após modificar todas as palavras
            time.sleep(0.001)


import random
import time

def executar_sistema(palavras, num_leitores, num_escritores, num_rodadas):
    tempos = []
    condicao = threading.Condition()

    for _ in range(num_rodadas):
        threads = []
        semaforo_leitura = threading.Semaphore(value=1)
        semaforo_escrita = threading.Semaphore(value=1)
        leitores = [0]
        escritores = threading.Lock()
        base_dados = BaseDeDados(palavras.copy())

        # Criação das threads
        for _ in range(num_leitores):
            thread = LeitorEscritorThread(f"Leitor-{_ + 1}", base_dados, semaforo_leitura, semaforo_escrita, leitores, escritores)
            threads.append(thread)

        for _ in range(num_escritores):
            thread = Escritor(f"Escritor-{_ + 1}", base_dados, semaforo_leitura, semaforo_escrita, leitores, escritores, condicao)
            threads.append(thread)

        # Embaralhamento das threads
        random.shuffle(threads)

        # Início da contagem do tempo
        start_time = time.time()

        # Início e término das threads
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Fim da contagem do tempo
        end_time = time.time()

        # Calcula o tempo de execução
        tempos.append(end_time - start_time)

    # Calcula o tempo médio de execução
    tempo_medio = sum(tempos) / len(tempos) if tempos else None

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
            print(f"Versão com Leitores e Escritores Tempo médio para {num_leitores} leitores e {num_escritores} escritores: {tempo_medio} segundos")

            # Escreva o tempo médio no arquivo
            f.write(f"{num_leitores} leitores, {num_escritores} escritores, tempo medio: {tempo_medio} segundos\n")

