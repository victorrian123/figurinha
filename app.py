import json
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

correcoes = {
    "PAM": "PAN", "BRASIL": "BRA", "ARGENTINA": "ARG",
    "ESTADOS": "USA", "AMERICA": "USA", "ALEMANHA": "GER",
    "FRANCA": "FRA", "FRANÇA": "FRA", "INGLATERRA": "ENG",
    "PORTUGAL": "POR", "ESPANHA": "ESP", "HOLANDA": "NED",
    "BELGICA": "BEL", "BÉLGICA": "BEL", "SUICA": "SUI",
    "SUÍÇA": "SUI", "CROACIA": "CRO", "CROÁCIA": "CRO",
    "NORUEGA": "NOR", "SUECIA": "SWE", "SUÉCIA": "SWE",
    "JAPAO": "JPN", "JAPÃO": "JPN", "COREIA": "KOR",
    "AUSTRALIA": "AUS", "AUSTRÁLIA": "AUS", "MEXICO": "MEX",
    "MÉXICO": "MEX", "COLOMBIA": "COL", "COLÔMBIA": "COL",
    "URUGUAI": "URU", "MARROCOS": "MAR", "TUNISIA": "TUN",
    "TUNÍSIA": "TUN", "TUNIS": "TUN", "TURQUIA": "TUR",
    "IRAQUE": "IRQ", "IRA": "IRN", "IRÃ": "IRN",
    "JORDANIA": "JOR", "JORDÂNIA": "JOR", "CANADA": "CAN",
    "CANADÁ": "CAN", "PANAMA": "PAN", "PANAMÁ": "PAN",
    "PARAGUAI": "PAR", "EQUADOR": "ECU", "EGITO": "EGY",
    "GANA": "GHA", "GHANA": "GHA", "AUSTRIA": "AUT",
    "ÁUSTRIA": "AUT", "ARGELIA": "ALG", "ARGÉLIA": "ALG",
    "ESCOCIA": "SCO", "ESCÓCIA": "SCO", "UZBEQUISTAO": "UZB",
    "UZBEQUISTÃO": "UZB", "REPUBLICA": "CZE", "CHECA": "CZE",
    "BOSNEA": "BIH", "BOSNIA": "BIH", "BÓSNIA": "BIH",
    "CATAR": "QAT", "QATAR": "QAT", "CABO": "CPV",
    "ARABIA": "KSA", "ARÁBIA": "KSA", "CONGO": "COD",
    "HAITI": "HAI", "MARFIM": "CIV", "AFRICA": "RSA", "SUL": "RSA",
    "NOVA": "NZL", "ZELANDIA": "NZL", "ZELÂNDIA": "NZL",
    "SENEGAL": "SEN",
}

numeros_extenso = {
    "UM": 1, "DOIS": 2, "TRÊS": 3, "TRES": 3,
    "QUATRO": 4, "CINCO": 5, "SEIS": 6, "SETE": 7,
    "OITO": 8, "NOVE": 9, "DEZ": 10, "ONZE": 11,
    "DOZE": 12, "TREZE": 13, "CATORZE": 14, "QUATORZE": 14,
    "QUINZE": 15, "DEZESSEIS": 16, "DEZESSETE": 17,
    "DEZOITO": 18, "DEZENOVE": 19, "VINTE": 20
}

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/consultar", methods=["POST"])
def consultar():
    body = request.json
    texto = body.get("texto", "").upper().strip()
    faltam = body.get("faltam", {})

    remover = False
    for gatilho in ["PEGUEI", "TENHO", "COLEI", "GANHEI", "TIREI"]:
        if texto.startswith(gatilho):
            texto = texto[len(gatilho):].strip()
            remover = True
            break

    dados = texto.split()
    if len(dados) < 2:
        return jsonify({"resposta": "Não entendi. Fale o país e o número."})

    sigla = dados[0]
    if sigla in correcoes:
        sigla = correcoes[sigla]

    valor = dados[1]
    try:
        numero = int(valor)
    except:
        numero = numeros_extenso.get(valor)

    if numero is None:
        return jsonify({"resposta": "Número não reconhecido."})

    if remover:
        if sigla in faltam and numero in faltam[sigla]:
            faltam[sigla].remove(numero)
            if not faltam[sigla]:
                del faltam[sigla]
                return jsonify({"resposta": f"{sigla} completo!", "faltam": faltam, "atualizado": True})
            return jsonify({"resposta": f"{sigla} {numero}: removido da lista", "faltam": faltam, "atualizado": True})
        return jsonify({"resposta": f"{sigla} {numero}: já estava marcado como completo", "faltam": faltam})

    if sigla in faltam:
        if numero in faltam[sigla]:
            return jsonify({"resposta": f"{sigla} {numero}: falta", "faltam": faltam})
        return jsonify({"resposta": f"{sigla} {numero}: você já tem", "faltam": faltam})
    return jsonify({"resposta": f"{sigla}: você já tem todas", "faltam": faltam})

HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Figurinhas Copa</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: sans-serif; background: #1a1a2e; color: #eee; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 20px; }
    h1 { color: #e94560; margin-bottom: 20px; font-size: 1.8rem; }
    #btn {
      width: 140px; height: 140px; border-radius: 50%; border: none;
      background: #e94560; color: white; font-size: 1rem; cursor: pointer;
      box-shadow: 0 0 20px rgba(233,69,96,0.5); transition: all 0.2s;
    }
    #btn.ouvindo { background: #0f3460; box-shadow: 0 0 30px rgba(15,52,96,0.8); animation: pulsar 1s infinite; }
    @keyframes pulsar { 0%,100% { transform: scale(1); } 50% { transform: scale(1.08); } }
    #resposta { margin-top: 30px; font-size: 1.5rem; font-weight: bold; text-align: center; min-height: 50px; color: #e94560; }
    #transcricao { margin-top: 10px; font-size: 0.9rem; color: #aaa; text-align: center; }
    #lista-container { margin-top: 30px; width: 100%; max-width: 500px; }
    h2 { color: #e94560; margin-bottom: 10px; }
    .pais { background: #16213e; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; }
    .pais strong { color: #e94560; }
    .numeros { color: #ccc; font-size: 0.95rem; }
  </style>
</head>
<body>
  <h1>⚽ Figurinhas Copa</h1>
  <button id="btn" onclick="toggleOuvir()">🎤<br>Iniciar</button>
  <div id="resposta">Pressione o botão para começar</div>
  <div id="transcricao"></div>
  <div id="lista-container">
    <h2>Figurinhas que faltam</h2>
    <div id="lista"></div>
  </div>

  <script>
    const _t20 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20];
    const FALTAM_INICIAL = {
      "FWC":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],
      "CC":[1,2,3,4,5,6,7,8,9,10,11,12,13,14],
      "ARG":[..._t20],"AUS":[..._t20],"AUT":[..._t20],"BEL":[..._t20],
      "BIH":[..._t20],"BRA":[..._t20],"CAN":[..._t20],"CIV":[..._t20],
      "COD":[..._t20],"COL":[..._t20],"CRO":[..._t20],"CZE":[..._t20],
      "ECU":[..._t20],"EGY":[..._t20],"ENG":[..._t20],"FRA":[..._t20],
      "GER":[..._t20],"GHA":[..._t20],"HAI":[..._t20],"IRN":[..._t20],
      "IRQ":[..._t20],"JOR":[..._t20],"JPN":[..._t20],"KOR":[..._t20],
      "KSA":[..._t20],"MAR":[..._t20],"MEX":[..._t20],"NED":[..._t20],
      "NOR":[..._t20],"NZL":[..._t20],"PAN":[..._t20],"PAR":[..._t20],
      "POR":[..._t20],"QAT":[..._t20],"RSA":[..._t20],"SCO":[..._t20],
      "SEN":[..._t20],"SUI":[..._t20],"SWE":[..._t20],"TUN":[..._t20],
      "TUR":[..._t20],"URU":[..._t20],"USA":[..._t20],"UZB":[..._t20],
    };

    function carregarFaltam() {
      const salvo = localStorage.getItem("faltam");
      return salvo ? JSON.parse(salvo) : JSON.parse(JSON.stringify(FALTAM_INICIAL));
    }

    function salvarFaltam(faltam) {
      localStorage.setItem("faltam", JSON.stringify(faltam));
    }

    function renderizarLista() {
      const faltam = carregarFaltam();
      const div = document.getElementById("lista");
      div.innerHTML = "";
      for (const [pais, nums] of Object.entries(faltam)) {
        div.innerHTML += `<div class="pais"><strong>${pais}</strong>: <span class="numeros">${nums.join(", ")}</span></div>`;
      }
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const rec = new SpeechRecognition();
    rec.lang = "pt-BR";
    rec.continuous = false;
    rec.interimResults = false;

    let ativo = false;
    let respondendo = false;

    // desbloqueio do audio no mobile — precisa rodar dentro de um toque
    let audioDesbloqueado = false;
    function desbloquearAudio() {
      if (audioDesbloqueado) return;
      const u = new SpeechSynthesisUtterance("");
      speechSynthesis.speak(u);
      audioDesbloqueado = true;
    }

    function toggleOuvir() {
      desbloquearAudio();
      if (ativo) {
        ativo = false;
        rec.stop();
        document.getElementById("btn").innerHTML = "🎤<br>Iniciar";
        document.getElementById("btn").classList.remove("ouvindo");
        document.getElementById("resposta").textContent = "Pausado.";
      } else {
        ativo = true;
        iniciarOuvir();
      }
    }

    function iniciarOuvir() {
      if (!ativo) return;
      document.getElementById("btn").classList.add("ouvindo");
      document.getElementById("btn").innerHTML = "⏹<br>Parar";
      try { rec.start(); } catch(e) {}
    }

    function falar(texto) {
      return new Promise(resolve => {
        // iOS Safari trava se a fila estiver cheia
        speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(texto);
        u.lang = "pt-BR";
        u.rate = 1;
        u.onend = resolve;
        u.onerror = resolve;
        speechSynthesis.speak(u);
        // fallback: se não disparar onend em 5s, continua
        setTimeout(resolve, 5000);
      });
    }

    rec.onresult = async (e) => {
      const texto = e.results[0][0].transcript;
      document.getElementById("transcricao").textContent = "Você falou: " + texto;
      respondendo = true;

      const faltam = carregarFaltam();
      const res = await fetch("/consultar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto, faltam })
      });
      const data = await res.json();
      document.getElementById("resposta").textContent = data.resposta;

      if (data.atualizado) {
        salvarFaltam(data.faltam);
        renderizarLista();
      }

      await falar(data.resposta);
      respondendo = false;
      iniciarOuvir();
    };

    rec.onend = () => {
      if (ativo && !respondendo) setTimeout(iniciarOuvir, 300);
    };

    rec.onerror = (e) => {
      if (e.error !== "no-speech" && e.error !== "aborted") console.error("Erro:", e.error);
      if (ativo && !respondendo) setTimeout(iniciarOuvir, 500);
    };

    renderizarLista();
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    import socket
    ip = socket.gethostbyname(socket.gethostname())
    print(f"\nAcesse no celular: http://{ip}:5001\n")
    app.run(host="0.0.0.0", port=5001, debug=False)
