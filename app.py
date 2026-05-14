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

def extrair_pares(tokens):
    """Extrai pares (sigla, numero) de uma lista de tokens como [BRASIL, 2, BRASIL, 3]"""
    pares = []
    i = 0
    sigla_atual = None
    while i < len(tokens):
        t = tokens[i]
        t_corrigido = correcoes.get(t, t)
        # Se parece ser uma sigla/país
        try:
            int(t)
            eh_numero = True
        except:
            eh_numero = False

        if not eh_numero:
            numero_extenso = numeros_extenso.get(t)
            if numero_extenso and sigla_atual:
                pares.append((sigla_atual, numero_extenso))
            else:
                sigla_atual = t_corrigido
        else:
            numero = int(t)
            if sigla_atual:
                pares.append((sigla_atual, numero))
        i += 1
    return pares

@app.route("/consultar", methods=["POST"])
def consultar():
    body = request.json
    texto = body.get("texto", "").upper().strip()
    faltam = body.get("faltam", {})

    remover = False
    for gatilho in ["PEGUEI", "TENHO", "COLEI", "GANHEI", "TIREI", "REMOVER", "TROQUEI"]:
        if texto.startswith(gatilho):
            texto = texto[len(gatilho):].strip()
            remover = True
            break

    tokens = texto.replace(",", " ").split()
    if len(tokens) < 2:
        return jsonify({"resposta": "Não entendi. Fale o país e o número."})

    pares = extrair_pares(tokens)
    if not pares:
        return jsonify({"resposta": "Não entendi. Fale o país e o número."})

    if remover:
        removidos = []
        completos = []
        for sigla, numero in pares:
            if sigla in faltam and numero in faltam[sigla]:
                faltam[sigla].remove(numero)
                if not faltam[sigla]:
                    del faltam[sigla]
                    completos.append(sigla)
                else:
                    removidos.append(f"{sigla} {numero}")
        if completos and not removidos:
            return jsonify({"resposta": ", ".join(completos) + " completo!", "faltam": faltam, "atualizado": True})
        if removidos:
            msg = ", ".join(removidos)
            if completos:
                msg += ". " + ", ".join(completos) + " completo!"
            else:
                msg += " removido" + ("s" if len(removidos) > 1 else "")
            return jsonify({"resposta": msg, "faltam": faltam, "atualizado": True})
        return jsonify({"resposta": "Já estavam marcadas como completas", "faltam": faltam})

    # consulta simples — só primeiro par
    sigla, numero = pares[0]
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
  <title>Figurinhas Copa 2026</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(160deg, #0a0a1a 0%, #1a1a2e 50%, #0d1b0d 100%);
      color: #eee;
      min-height: 100vh;
      padding-bottom: 100px;
    }

    /* Header */
    #header {
      background: linear-gradient(135deg, #1a3a1a, #0f3460, #1a3a1a);
      padding: 20px;
      text-align: center;
      border-bottom: 2px solid #2a6a2a;
      position: sticky; top: 0; z-index: 10;
    }
    #header h1 { font-size: 1.6rem; color: #f5c518; text-shadow: 0 0 10px rgba(245,197,24,0.4); }
    #header h1 span { color: #4caf50; }
    #contador { font-size: 0.85rem; color: #aaa; margin-top: 4px; }
    #contador b { color: #f5c518; }
    #barra-fundo { height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; margin-top: 8px; }
    #barra { height: 6px; background: linear-gradient(90deg, #4caf50, #f5c518); border-radius: 3px; transition: width 0.5s ease; }

    /* Main */
    #main { max-width: 600px; margin: 0 auto; padding: 16px; }

    /* Resposta */
    #resposta-box {
      background: rgba(245,197,24,0.08);
      border: 1px solid rgba(245,197,24,0.2);
      border-radius: 12px;
      padding: 14px 16px;
      margin-bottom: 16px;
      min-height: 52px;
      display: flex; align-items: center; justify-content: center;
    }
    #resposta { font-size: 1.2rem; font-weight: bold; color: #f5c518; text-align: center; }
    #transcricao { font-size: 0.8rem; color: #666; text-align: center; margin-top: 4px; }

    /* Busca e WhatsApp */
    #toolbar { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
    #toolbar-linha2 { display: flex; gap: 8px; margin-bottom: 14px; }
    #busca {
      flex: 1; padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);
      background: rgba(255,255,255,0.06); color: #eee; font-size: 0.95rem; outline: none;
    }
    #busca::placeholder { color: #555; }
    #busca:focus { border-color: rgba(245,197,24,0.4); background: rgba(255,255,255,0.09); }
    #ordem {
      padding: 10px 10px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);
      background: rgba(255,255,255,0.06); color: #eee; font-size: 0.85rem; outline: none; cursor: pointer;
    }
    #btn-pix {
      padding: 10px 14px; border-radius: 10px; border: none;
      background: linear-gradient(135deg, #00b4d8, #0077b6); color: white;
      font-size: 0.9rem; cursor: pointer; white-space: nowrap; font-weight: bold;
    }
    #modal-pix {
      display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7);
      align-items: center; justify-content: center; z-index: 200;
    }
    #modal-pix-box {
      background: #16213e; border-radius: 16px; padding: 28px 24px;
      max-width: 320px; width: 90%; text-align: center;
      border: 1px solid rgba(255,255,255,0.1);
    }
    #modal-pix-box h3 { color: #f5c518; margin-bottom: 8px; font-size: 1.2rem; }
    #modal-pix-box p { color: #aaa; font-size: 0.9rem; margin-bottom: 16px; }
    #pix-chave {
      background: rgba(255,255,255,0.08); border-radius: 8px; padding: 12px;
      font-size: 0.95rem; color: #eee; word-break: break-all; margin-bottom: 14px;
      border: 1px solid rgba(255,255,255,0.15);
    }
    #btn-copiar-pix {
      width: 100%; padding: 12px; border-radius: 10px; border: none;
      background: linear-gradient(135deg, #00b4d8, #0077b6);
      color: white; font-size: 1rem; cursor: pointer; font-weight: bold; margin-bottom: 10px;
    }
    #btn-fechar-pix {
      width: 100%; padding: 10px; border-radius: 10px; border: none;
      background: rgba(255,255,255,0.06); color: #aaa; font-size: 0.9rem; cursor: pointer;
    }
    #btn-whatsapp {
      padding: 10px 14px; border-radius: 10px; border: none;
      background: #25d366; color: white; font-size: 0.9rem; cursor: pointer;
      white-space: nowrap; font-weight: bold;
    }

    /* Cards de país */
    .pais {
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 12px;
      padding: 12px 14px;
      margin-bottom: 8px;
      transition: border-color 0.2s;
    }
    .pais:hover { border-color: rgba(245,197,24,0.3); }
    .pais-header { display: flex; align-items: center; gap: 8px; cursor: pointer; user-select: none; }
    .pais-header strong { color: #f5c518; font-size: 1rem; flex: 1; }
    .pais-mini-barra-fundo { width: 60px; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; }
    .pais-mini-barra { height: 4px; background: linear-gradient(90deg, #e94560, #f5c518); border-radius: 2px; transition: width 0.3s; }
    .qtd { font-size: 0.75rem; color: #888; }
    .seta { font-size: 0.7rem; color: #555; transition: transform 0.2s; }
    .pais-header.fechado .seta { transform: rotate(-90deg); }
    .numeros { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
    .numeros.oculto { display: none; }
    .num {
      background: rgba(15,52,96,0.8);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 8px; padding: 5px 11px;
      font-size: 0.9rem; cursor: pointer;
      transition: all 0.15s; user-select: none; font-weight: bold;
    }
    .num:hover { background: #e94560; border-color: #e94560; transform: scale(1.1); }
    .num.removendo { animation: sumir 0.3s forwards; }
    @keyframes sumir { to { opacity: 0; transform: scale(0.5); } }

    /* Completos */
    .secao-completos {
      display: flex; align-items: center; gap: 8px;
      color: #4caf50; font-weight: bold; margin: 20px 0 10px;
      font-size: 0.95rem;
    }
    .secao-completos::before, .secao-completos::after {
      content: ""; flex: 1; height: 1px; background: rgba(76,175,80,0.3);
    }
    .pais.completo {
      background: rgba(76,175,80,0.07);
      border-color: rgba(76,175,80,0.25);
    }
    .pais.completo .pais-header strong { color: #4caf50; }

    /* Botão flutuante */
    #btn-fixo {
      position: fixed; bottom: 24px; right: 24px;
      width: 70px; height: 70px; border-radius: 50%; border: none;
      background: linear-gradient(135deg, #e94560, #c0392b);
      color: white; font-size: 1.8rem; cursor: pointer;
      box-shadow: 0 4px 20px rgba(233,69,96,0.6);
      transition: all 0.2s; z-index: 100;
      display: flex; align-items: center; justify-content: center;
    }
    #btn-fixo.ouvindo {
      background: linear-gradient(135deg, #0f3460, #1a5276);
      box-shadow: 0 4px 25px rgba(15,52,96,0.8);
      animation: pulsar 1s infinite;
    }
    #btn-label {
      position: fixed; bottom: 100px; right: 16px;
      font-size: 0.75rem; color: #aaa; text-align: center; width: 86px;
    }
    @keyframes pulsar { 0%,100% { transform: scale(1); } 50% { transform: scale(1.1); } }

    /* Splash */
    #splash {
      position: fixed; inset: 0; background: linear-gradient(160deg, #0a0a1a, #1a3a1a);
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      z-index: 999; transition: opacity 0.6s;
    }
    #splash h1 { font-size: 3rem; color: #f5c518; margin-bottom: 8px; }
    #splash p { color: #aaa; font-size: 1rem; }
    #splash.saindo { opacity: 0; pointer-events: none; }

    h2 { color: #f5c518; margin-bottom: 10px; font-size: 1rem; text-transform: uppercase; letter-spacing: 1px; }
  </style>
</head>
<body>

  <!-- Splash -->
  <div id="splash">
    <h1>⚽</h1>
    <h1 style="font-size:1.8rem;margin-bottom:4px">Figurinhas Copa</h1>
    <p>2026</p>
  </div>

  <!-- Header fixo -->
  <div id="header">
    <h1>⚽ Figurinhas <span>Copa 2026</span></h1>
    <div id="contador">Você tem <b><span id="qtd-tem">0</span></b> de <b><span id="qtd-total">914</span></b> figurinhas</div>
    <div id="barra-fundo"><div id="barra" style="width:0%"></div></div>
  </div>

  <!-- Conteúdo -->
  <div id="main">
    <div id="resposta-box">
      <div>
        <div id="resposta">Toque no microfone para começar</div>
        <div id="transcricao"></div>
      </div>
    </div>

    <div id="toolbar">
      <input id="busca" type="text" placeholder="🔍 Buscar país..." oninput="renderizarLista()">
    </div>
    <div id="toolbar-linha2">
      <select id="ordem" onchange="renderizarLista()" style="flex:1">
        <option value="nome">A-Z</option>
        <option value="faltando">Mais faltam</option>
        <option value="progresso">Mais completo</option>
      </select>
      <button id="btn-whatsapp" onclick="compartilhar()">📲 WhatsApp</button>
      <button id="btn-pix" onclick="document.getElementById('modal-pix').style.display='flex'">☕ PIX</button>
    </div>

    <h2>Figurinhas que faltam</h2>
    <div id="lista"></div>
  </div>

  <!-- Modal PIX -->
  <div id="modal-pix" onclick="if(event.target===this)this.style.display='none'">
    <div id="modal-pix-box">
      <h3>☕ Apoiar o projeto</h3>
      <p>Se o app te ajudou a completar o álbum, considere um cafézinho!</p>
      <div id="pix-chave">victor.rian@hotmail.com</div>
      <button id="btn-copiar-pix" onclick="navigator.clipboard.writeText('victor.rian@hotmail.com').then(()=>{this.textContent='✅ Copiado!';setTimeout(()=>this.textContent='📋 Copiar chave PIX',2000)})">📋 Copiar chave PIX</button>
      <button id="btn-fechar-pix" onclick="document.getElementById('modal-pix').style.display='none'">Fechar</button>
    </div>
  </div>

  <!-- Botão flutuante -->
  <div id="btn-label">Microfone</div>
  <button id="btn-fixo" onclick="toggleOuvir()">🎤</button>

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


    const PAISES = {
      "FWC": ["🏆", "FIFA World Cup"],
      "CC":  ["🇨🇼", "Curaçao"],
      "ARG": ["🇦🇷", "Argentina"],
      "AUS": ["🇦🇺", "Austrália"],
      "AUT": ["🇦🇹", "Áustria"],
      "BEL": ["🇧🇪", "Bélgica"],
      "BIH": ["🇧🇦", "Bósnia e Herzegovina"],
      "BRA": ["🇧🇷", "Brasil"],
      "CAN": ["🇨🇦", "Canadá"],
      "CIV": ["🇨🇮", "Costa do Marfim"],
      "COD": ["🇨🇩", "R.D. Congo"],
      "COL": ["🇨🇴", "Colômbia"],
      "CRO": ["🇭🇷", "Croácia"],
      "CZE": ["🇨🇿", "Tchéquia"],
      "ECU": ["🇪🇨", "Equador"],
      "EGY": ["🇪🇬", "Egito"],
      "ENG": ["🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Inglaterra"],
      "FRA": ["🇫🇷", "França"],
      "GER": ["🇩🇪", "Alemanha"],
      "GHA": ["🇬🇭", "Gana"],
      "HAI": ["🇭🇹", "Haiti"],
      "IRN": ["🇮🇷", "Irã"],
      "IRQ": ["🇮🇶", "Iraque"],
      "JOR": ["🇯🇴", "Jordânia"],
      "JPN": ["🇯🇵", "Japão"],
      "KOR": ["🇰🇷", "Coreia do Sul"],
      "KSA": ["🇸🇦", "Arábia Saudita"],
      "MAR": ["🇲🇦", "Marrocos"],
      "MEX": ["🇲🇽", "México"],
      "NED": ["🇳🇱", "Holanda"],
      "NOR": ["🇳🇴", "Noruega"],
      "NZL": ["🇳🇿", "Nova Zelândia"],
      "PAN": ["🇵🇦", "Panamá"],
      "PAR": ["🇵🇾", "Paraguai"],
      "POR": ["🇵🇹", "Portugal"],
      "QAT": ["🇶🇦", "Catar"],
      "RSA": ["🇿🇦", "África do Sul"],
      "SCO": ["🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Escócia"],
      "SEN": ["🇸🇳", "Senegal"],
      "SUI": ["🇨🇭", "Suíça"],
      "SWE": ["🇸🇪", "Suécia"],
      "TUN": ["🇹🇳", "Tunísia"],
      "TUR": ["🇹🇷", "Turquia"],
      "URU": ["🇺🇾", "Uruguai"],
      "USA": ["🇺🇸", "Estados Unidos"],
      "UZB": ["🇺🇿", "Uzbequistão"],
    };
    function carregarFaltam() {
      const salvo = localStorage.getItem("faltam");
      return salvo ? JSON.parse(salvo) : JSON.parse(JSON.stringify(FALTAM_INICIAL));
    }

    function salvarFaltam(faltam) {
      localStorage.setItem("faltam", JSON.stringify(faltam));
    }

    const TOTAL = Object.values(FALTAM_INICIAL).reduce((s, v) => s + v.length, 0);
    document.getElementById("qtd-total").textContent = TOTAL;

    function contarTem(faltam) {
      const faltando = Object.values(faltam).reduce((s, v) => s + v.length, 0);
      return TOTAL - faltando;
    }

    function atualizarContador(faltam) {
      const tem = contarTem(faltam);
      document.getElementById("qtd-tem").textContent = tem;
      document.getElementById("barra").style.width = (tem / TOTAL * 100).toFixed(1) + "%";
    }

    function togglePais(header) {
      header.classList.toggle("fechado");
      header.nextElementSibling.classList.toggle("oculto");
    }

    function tocarSomCompleto() {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const notas = [523, 659, 784, 1047]; // C, E, G, C oitava acima
      notas.forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.frequency.value = freq;
        osc.type = "sine";
        gain.gain.setValueAtTime(0.3, ctx.currentTime + i * 0.12);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.12 + 0.4);
        osc.start(ctx.currentTime + i * 0.12);
        osc.stop(ctx.currentTime + i * 0.12 + 0.4);
      });
    }

    function tocarSomRemocao() {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.value = 880;
      osc.type = "sine";
      gain.gain.setValueAtTime(0.15, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.15);
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.15);
    }

    function removerComAnim(pais, numero) {
      const el = document.getElementById(`n-${pais}-${numero}`);
      if (el) {
        el.classList.add("removendo");
        setTimeout(() => removerFigurinha(pais, numero), 280);
      } else {
        removerFigurinha(pais, numero);
      }
    }

    function removerFigurinha(pais, numero) {
      const faltam = carregarFaltam();
      if (faltam[pais]) {
        faltam[pais] = faltam[pais].filter(n => n !== numero);
        if (faltam[pais].length === 0) {
          delete faltam[pais];
          salvarFaltam(faltam);
          renderizarLista();
          tocarSomCompleto();
        } else {
          salvarFaltam(faltam);
          renderizarLista();
          tocarSomRemocao();
        }
      }
    }

    function renderizarLista() {
      const faltam = carregarFaltam();
      atualizarContador(faltam);
      const filtro = (document.getElementById("busca")?.value || "").toUpperCase().trim();
      const div = document.getElementById("lista");
      div.innerHTML = "";

      const completos = [];
      for (const sigla of Object.keys(FALTAM_INICIAL)) {
        if (!faltam[sigla]) completos.push(sigla);
      }

      // Ordenação
      const ordem = document.getElementById("ordem")?.value || "nome";
      let entradas = Object.entries(faltam);
      if (ordem === "nome") {
        entradas.sort((a, b) => a[0].localeCompare(b[0]));
      } else if (ordem === "faltando") {
        entradas.sort((a, b) => b[1].length - a[1].length);
      } else if (ordem === "progresso") {
        entradas.sort((a, b) => {
          const totalA = FALTAM_INICIAL[a[0]] ? FALTAM_INICIAL[a[0]].length : 20;
          const totalB = FALTAM_INICIAL[b[0]] ? FALTAM_INICIAL[b[0]].length : 20;
          return (a[1].length / totalA) - (b[1].length / totalB);
        });
      }

      // Times com figurinhas faltando
      for (const [pais, nums] of entradas) {
        const nome = PAISES[pais] ? `${PAISES[pais][0]} ${PAISES[pais][1]}` : pais;
        if (filtro && !pais.includes(filtro) && !nome.toUpperCase().includes(filtro)) continue;
        const total_pais = FALTAM_INICIAL[pais] ? FALTAM_INICIAL[pais].length : 20;
        const perc = ((total_pais - nums.length) / total_pais * 100).toFixed(0);
        const botoes = nums.map(n => `<span class="num" id="n-${pais}-${n}" onclick="removerComAnim('${pais}', ${n})">${n}</span>`).join("");
        div.innerHTML += `<div class="pais"><div class="pais-header" onclick="togglePais(this)"><strong>${nome}</strong><div class="pais-mini-barra-fundo"><div class="pais-mini-barra" style="width:${perc}%"></div></div><span class="qtd">${nums.length}</span><span class="seta">▼</span></div><div class="numeros">${botoes}</div></div>`;
      }

      // Times completos
      const filtrados = completos.filter(s => {
        if (!filtro) return true;
        const nome = PAISES[s] ? PAISES[s][1] : s;
        return s.includes(filtro) || nome.toUpperCase().includes(filtro);
      });
      if (filtrados.length > 0) {
        div.innerHTML += `<div class="secao-completos">✅ Completos (${filtrados.length})</div>`;
        for (const sigla of filtrados) {
          const nome = PAISES[sigla] ? `${PAISES[sigla][0]} ${PAISES[sigla][1]}` : sigla;
          div.innerHTML += `<div class="pais completo"><strong>${nome}</strong></div>`;
        }
      }
    }

    function compartilhar() {
      const faltam = carregarFaltam();
      const tem = contarTem(faltam);
      let msg = `⚽ Figurinhas Copa - tenho ${tem}/${TOTAL}\\n\\nFaltam:\\n`;
      for (const [pais, nums] of Object.entries(faltam)) {
        msg += `${pais}: ${nums.join(", ")}\\n`;
      }
      const url = "https://wa.me/?text=" + encodeURIComponent(msg);
      window.open(url, "_blank");
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
        document.getElementById("btn-fixo").textContent = "🎤";
        document.getElementById("btn-fixo").classList.remove("ouvindo");
        document.getElementById("btn-label").textContent = "Microfone";
        document.getElementById("resposta").textContent = "Pausado.";
      } else {
        ativo = true;
        iniciarOuvir();
      }
    }

    function iniciarOuvir() {
      if (!ativo) return;
      document.getElementById("btn-fixo").classList.add("ouvindo");
      document.getElementById("btn-fixo").textContent = "⏹";
      document.getElementById("btn-label").textContent = "Parar";
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

    // Toque na caixa de resposta liga/desliga o microfone
    document.getElementById("resposta-box").addEventListener("click", () => {
      toggleOuvir();
    });

    // Splash
    setTimeout(() => {
      document.getElementById("splash").classList.add("saindo");
      setTimeout(() => document.getElementById("splash").remove(), 700);
    }, 1200);
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    import socket
    ip = socket.gethostbyname(socket.gethostname())
    print(f"\nAcesse no celular: http://{ip}:5001\n")
    app.run(host="0.0.0.0", port=5001, debug=False)
