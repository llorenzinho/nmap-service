# nmap-service

Servizio REST API che espone scansioni nmap come job asincroni. Il client invia un target e un tipo di scansione, riceve un ID job e può interrogare lo stato fino al completamento. Le scansioni vengono eseguite in modo concorrente tramite un pool di thread o processi configurabile.

## Indice

- [1. Descrizione generale](#1-descrizione-generale)
- [2. Installazione (Docker Compose)](#2-installazione-docker-compose)
  - [2.1 Requisiti](#21-requisiti)
  - [2.2 Installazione](#22-installazione)
- [3. Sviluppo](#3-sviluppo)
  - [3.1 Requisiti](#31-requisiti)
  - [3.2 Pre-commit](#32-pre-commit)
  - [3.3 Avvio in modalità sviluppo](#33-avvio-in-modalità-sviluppo)
- [4. Testare le API con Bruno](#4-testare-le-api-con-bruno)
- [5. Esempi con curl](#5-esempi-con-curl)
- [6. Scelte tecniche](#6-scelte-tecniche)

---

## 1. Descrizione generale

**nmap-service** espone `nmap` tramite una API HTTP costruita con [FastAPI](https://fastapi.tiangolo.com/). Ogni scansione viene salvata come job in un database PostgreSQL ed eseguita in modo asincrono. L'API permette di:

- Sottomettere un job di scansione (`QUICK`, `FULL` o `SERVICE_DETECTION`)
- Elencare tutti i job e i loro stati
- Recuperare i risultati di un job completato

**Stack tecnologico:** Python 3.13 · FastAPI · SQLModel · PostgreSQL · uvicorn · Docker

---

## 2. Installazione (Docker Compose)

### 2.1 Requisiti

- [Docker](https://docs.docker.com/get-docker/) >= 29.2.1
- [Docker Compose](https://docs.docker.com/compose/) >= v5.1.0 (plugin, non standalone)

### 2.2 Installazione

1. Clonare il repository:

```bash
git clone <repo-url>
cd nmap-service
```

2. Avviare lo stack:

```bash
docker compose up --build
```

L'API sarà disponibile su `http://localhost:3000`.

**Servizi avviati:**

| Servizio   | Porta | Descrizione              |
|------------|-------|--------------------------|
| `api`      | 3000  | Applicazione FastAPI     |
| `postgres` | 5432  | Database PostgreSQL 18   |

**Variabili d'ambiente** (configurabili in `docker-compose.yaml`):

| Variabile                       | Default    | Descrizione                                      |
|---------------------------------|------------|--------------------------------------------------|
| `APP_DB__USER`                  | `postgres` | Utente del database                              |
| `APP_DB__PASSWORD`              | `postgres` | Password del database                            |
| `APP_DB__HOST`                  | `postgres` | Host del database                                |
| `APP_DB__PORT`                  | `5432`     | Porta del database                               |
| `APP_DB__DB`                    | `nmap`     | Nome del database                                |
| `APP_SERVER__HOST`              | `0.0.0.0`  | Host di ascolto dell'API                         |
| `APP_SERVER__PORT`              | `3000`     | Porta di ascolto dell'API                        |
| `APP_LOG__LEVEL`                | `INFO `    | Livello di log                                   |
| `APP_RUNNER__TIMEOUT`           | `300`      | Timeout delle scansioni nmap (secondi)           |
| `APP_SCAN_STRATEGY__STRATEGY`   | `THREAD`   | Strategia di esecuzione (`THREAD` / `PROCESS`)   |
| `APP_SCAN_STRATEGY__N_EXECUTOR` | `4`        | Numero di worker concorrenti                     |

---

## 3. Sviluppo

### 3.1 Requisiti

- Python >= 3.13
- [Poetry](https://python-poetry.org/) >= 2.2
- [invoke](https://www.pyinvoke.org/) (incluso nelle dipendenze dev)
- Docker Compose (per il database)

Installare le dipendenze:

```bash
poetry install
```

### 3.2 Pre-commit

Il progetto usa [pre-commit](https://pre-commit.com/) con due hook:

| Hook                      | Stage       | Descrizione                                                |
|---------------------------|-------------|------------------------------------------------------------|
| `Format Code`             | `pre-push`  | Esegue `autoflake`, `isort` e `black` tramite `inv swag`   |
| `conventional-pre-commit` | `commit-msg`| Impone il formato [Conventional Commits](https://www.conventionalcommits.org/) |

Installare gli hook:

```bash
poetry run pre-commit install
```

Eseguire il formatter manualmente:

```bash
poetry run inv swag
```

### 3.3 Avvio in modalità sviluppo

Avviare in modalità watch:

```bash
docker compose up --build -w
```

Le modifiche a `src/` vengono sincronizzate istantaneamente e uvicorn si riavvia automaticamente. Le modifiche a `pyproject.toml` o `poetry.lock` provocano una ricostruzione completa dell'immagine.

---

## 4. Testare le API con Bruno

La collection [Bruno](https://www.usebruno.com/) si trova nella cartella `bruno/` e contiene le richieste pronte per testare tutti gli endpoint.

### Requisiti

- [Bruno](https://www.usebruno.com/downloads) >= 3.1.3

### Struttura della collection

```
bruno/
├── environments/
│   └── local.bru            # Variabili d'ambiente (baseUrl, scan_id)
└── scans/
    ├── submit-scan.bru      # POST /api/v1/scans
    ├── list-scans.bru       # GET  /api/v1/scans
    └── get-scan-results.bru # GET /api/v1/scans/:scan_id/results
```

### Utilizzo

1. Aprire Bruno e importare la cartella `bruno/`
2. Selezionare l'ambiente **local** (in alto a destra)
3. Eseguire le richieste nell'ordine suggerito dalla sequenza (`seq`):

| # | Richiesta           | Metodo | Endpoint                              | Descrizione                         |
|---|---------------------|--------|---------------------------------------|-------------------------------------|
| 1 | Submit Scan         | POST   | `/api/v1/scans`                       | Avvia una scansione, salva `scan_id`|
| 2 | List Scans          | GET    | `/api/v1/scans`                       | Elenca tutti i job                  |
| 3 | Get Scan Results    | GET    | `/api/v1/scans/:scan_id/results`      | Recupera lo stato                   |
| 3 | Get Scan Results    | GET    | `/api/v1/scans/:scan_id/results`      | Recupera i risultati                |

### Tipi di scansione disponibili

| `scan_type`          | Flag nmap  | Descrizione                        |
|----------------------|------------|------------------------------------|
| `QUICK`              | `-T4 -F`   | Scansione rapida delle porte comuni |
| `FULL`               | `-T4 -p-`  | Scansione completa di tutte le porte |
| `SERVICE_DETECTION`  | `-sV`      | Rilevamento versione dei servizi   |

> Dopo l'esecuzione di **Submit Scan**, la variabile `scan_id` viene salvata automaticamente nell'ambiente tramite lo script post-response, e viene usata direttamente da **Get Scan Results**.


## 5. Esempi con curl

Flusso completo di utilizzo dell'API dalla riga di comando.

**Requirements**

- curl
- jq

### 1. Avviare una scansione

```bash
export id=$(curl -s -X POST http://localhost:3000/api/v1/scans \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1", "scan_type": "QUICK"}')
```

Risposta (scan_id):
```
"1022f31a-f571-426d-b185-2c85b5574897"
```

### 2. Verificare lo stato del job

Subito dopo la submit il job sarà in stato `pending` o `running`:

```bash
curl -s http://localhost:3000/api/v1/scans/$id | jq
```

Risposta mentre la scansione è in corso:
```json
{
  "status": "running",
  "summary": null
}
```

Risposta con scansione completata:
```json
{
  "status": "completed",
  "summary": {
    "target": "127.0.0.1",
    "num_ports": 3,
    "elapsed_seconds": 4.21
  }
}
```

In caso di errore:
```json
{
  "status": "failed",
  "summary": {
    "message": "nmap returned 1.\ncmd: nmap -T4 -F -oX - 127.0.0.1\nstderr: ..."
  }
}
```

### 3. Recuperare i risultati quando completato

Ripetere la chiamata fino a quando `status` è `completed`:

```bash
curl -s http://localhost:3000/api/v1/scans/$id/results | jq
```

```json
{
  "target": "127.0.0.1",
  "start": "2026-03-10T19:10:41.785453",
  "end": "2026-03-10T19:10:42.144387",
  "command": "nmap -T4 -F -oX - 127.0.0.1",
  "result": [
    {
      "ip": "127.0.0.1",
      "open_ports": [
        {
          "port": 3000,
          "protocol": "tcp",
          "service": "ppp"
        }
      ]
    }
  ]
}
```

### 4. Elencare tutti i job

```bash
curl -s http://localhost:3000/api/v1/scans
```

Risposta:
```json
[
  {
    "id": "1022f31a-f571-426d-b185-2c85b5574897",
    "timestamp": "2026-03-10T10:00:01.000000",
    "status": "completed"
  },
  {
    "id": "bf112345-1a2b-3c4d-5e6f-7a8b9c0d1e2f",
    "timestamp": "2026-03-10T10:05:00.000000",
    "status": "running"
  }
]
```

---

## 6. Scelte tecniche

### Futures al posto di BackgroundTasks di FastAPI

FastAPI espone `BackgroundTasks` come meccanismo nativo per eseguire operazioni dopo la risposta HTTP. Tuttavia questo strumento è progettato per task brevi e leggeri (invio email, log, notifiche): gira nello stesso event loop asincrono del server e non offre né parallelismo reale né isolamento degli errori. Una scansione nmap può durare decine di secondi o minuti, e bloccare o saturare l'event loop avrebbe un impatto diretto sulla latenza di tutte le altre richieste.

Per questo si è scelto di usare `concurrent.futures` (`ThreadPoolExecutor` / `ProcessPoolExecutor`), che delegano l'esecuzione a worker separati e restituiscono un `Future` su cui registrare callback di completamento ed errore. Il server HTTP rimane completamente libero durante tutta la durata della scansione.

### Pattern Strategy per l'esecuzione dei job

L'esecuzione dei job è astratta dietro un'interfaccia `ScanStrategy`. Attualmente è implementata `LocalScanStrategy`, che usa un pool locale (thread o processi), ma il pattern è stato scelto esplicitamente per rendere semplice aggiungere in futuro strategie alternative senza toccare il resto del codice:

- `DockerStrategy` — ogni scansione in un container isolato
- `KubernetesJobStrategy` — job K8s per ambienti cloud-native
- `ECSTaskStrategy` — task Amazon ECS per deployment su AWS

Aggiungere una nuova strategia significa implementare un'unica classe concreta con il metodo `launch()` e registrarla nella dependency injection.

### ProcessPoolExecutor e la scelta di PostgreSQL

`ProcessPoolExecutor` garantisce parallelismo reale. Tuttavia i processi non condividono memoria: un database in-memory (SQLite in-process, dizionari condivisi) non sarebbe accessibile dai worker figli.

Questa limitazione ha motivato la scelta di PostgreSQL come storage persistente fin dall'inizio, anche in assenza di un requisito esplicito. Il database esterno risolve il problema di condivisione dello stato ed è la scelta corretta per qualsiasi deployment reale. Entrambe le strategie (`THREAD` e `PROCESS`) sono configurabili tramite variabile d'ambiente senza modificare il codice.

### Dependency Injection con FastAPI

Tutta la costruzione delle dipendenze (`NmapRunner`, `ScanStrategy`, `NmapJobRepository`, `ScanManager`) è gestita tramite il sistema di `Depends` di FastAPI. I pool di thread e processi sono singleton ottenuti con `@lru_cache`, garantendo che vengano creati una sola volta per tutto il ciclo di vita dell'applicazione.

In alternativa si sarebbe potuto adottare un framework di DI dedicato (come `dependency-injector`) per avere un container esplicito, lifecycle management più granulare e migliore testabilità tramite override del container. Per la complessità attuale del progetto il sistema nativo di FastAPI è sufficiente, ma rimane un'evoluzione naturale qualora il numero di dipendenze dovesse crescere.
