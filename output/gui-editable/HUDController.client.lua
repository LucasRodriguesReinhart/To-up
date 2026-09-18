-- Layouts e templates são editados em StarterGui.MinaHUD.
-- Este controlador apenas conecta ações, preenche dados e anima estados.
local RS=game:GetService("ReplicatedStorage")
local Players=game:GetService("Players")
local TS=game:GetService("TweenService")
local UIS=game:GetService("UserInputService")
local player=Players.LocalPlayer
local tela=script.Parent
local canvas=tela:WaitForChild("ResponsiveHUD")
local templates=tela:WaitForChild("Templates")
local Config=require(RS:WaitForChild("Config"))
local R=RS:WaitForChild("Remotes")
local dados=nil
local function clone(name,parent)
 local obj=templates:WaitForChild(name):Clone()
 obj.Visible=true
 obj:SetAttribute("GeradoPeloControlador",true)
 obj.Parent=parent
 return obj
end
local function limparGerados(parent)
 for _,obj in parent:GetChildren() do
  if obj:GetAttribute("GeradoPeloControlador") then obj:Destroy() end
 end
end
local hud=canvas.Moedas
local lblMoeda=hud.Valor
local lblDano=hud.Dano
local bag=canvas.Mochila
local lblMochila=bag.Capacidade
local barraMochila=bag.BarraFundo.Preenchimento
local corBarra=barraMochila.BackgroundColor3
local avisos=canvas.Avisos
local function avisar(texto,cor)
 local f=clone("Aviso",avisos)
 f.Texto.Text=texto
 if cor then f.Texto.TextColor3=cor end
 task.delay(2.2,function()
  if not f.Parent then return end
  TS:Create(f,TweenInfo.new(.4),{BackgroundTransparency=1}):Play()
  TS:Create(f.Texto,TweenInfo.new(.4),{TextTransparency=1}):Play()
  task.wait(.45)
  f:Destroy()
 end)
end
local function formatar(n)
	if n >= 1e9 then return string.format("%.1fB", n / 1e9) end
	if n >= 1e6 then return string.format("%.1fM", n / 1e6) end
	if n >= 1e3 then return string.format("%.1fK", n / 1e3) end
	return tostring(math.floor(n))
end

local atualizarUI  -- definida mais abaixo (UI do Ignis tambem depende)

local function atualizarHUD()
	if not dados then return end
	lblMoeda.Text = "$ " .. formatar(dados.moeda)
	lblMochila.Text = string.format("Mochila %d/%d", dados.carregado, dados.capacidade)
	local frac = dados.capacidade > 0 and dados.carregado / dados.capacidade or 0
	TS:Create(barraMochila, TweenInfo.new(0.2), { Size = UDim2.fromScale(math.min(frac, 1), 1) }):Play()
	barraMochila.BackgroundColor3 = frac >= 1 and barraMochila:GetAttribute("CorCheia") or corBarra
	lblDano.Text = string.format("Dano %.1f", dados.dano)
end

-- ================= BARREIRAS =================
-- libera localmente a barreira das areas que o jogador ja desbloqueou
local function atualizarBarreiras()
	if not dados then return end
	local areas = workspace:FindFirstChild("Areas")
	if not areas then return end
	for _, d in ipairs(areas:GetDescendants()) do
		if d:IsA("BasePart") and d.Name == "Barreira" then
			local precisa = d:GetAttribute("LiberaComArea")
			local liberada = precisa and dados.areas[precisa] == true
			d.CanCollide = not liberada
            d.Transparency = liberada and 0.9 or 0.65
		end
	end
end

R.AtualizarDados.OnClientEvent:Connect(function(novo)
	dados = novo
	atualizarHUD()
	atualizarBarreiras()
	if atualizarUI then atualizarUI() end
end)

R.FeedbackMina.OnClientEvent:Connect(function(info)
	if info.tipo == "hat" then
		local r = Config.Raridades[info.raridade]
		avisar((info.novo and "NOVO! " or "") .. info.texto .. " (" .. r.nome .. ")", r.cor)
	elseif info.tipo == "cheia" then
		avisar(info.texto, Color3.fromRGB(255, 110, 90))
	elseif info.tipo == "area" then
		avisar(info.texto, Color3.fromRGB(120, 230, 140))
	elseif info.tipo == "bloqueada" then
		avisar(info.texto, Color3.fromRGB(255, 160, 60))
	end
end)

task.spawn(function()
	-- AreaAtmosphere owns playback and per-island music.
	dados = R.PedirDados:InvokeServer()
	atualizarHUD()
	atualizarBarreiras()
	if atualizarUI then atualizarUI() end
end)

-- ================= BASE DE PAINEIS =================
local VERDE   = Color3.fromRGB(55, 160, 85)
local AZUL    = Color3.fromRGB(55, 120, 200)
local LARANJA = Color3.fromRGB(200, 120, 45)
local ROXO    = Color3.fromRGB(140, 70, 210)

local Sons = RS:WaitForChild("Sons")
local Debris = game:GetService("Debris")
local function tocar(nome)
	local base = Sons:FindFirstChild(nome)
	if not base then return end
	local c = base:Clone()
	c.Parent = game:GetService("SoundService")
	c:Play()
	Debris:AddItem(c, 5)
end

local function chamar(remote, arg)
	local res = remote:InvokeServer(arg)
	if res and res.msg then
		avisar(res.msg, res.ok and Color3.fromRGB(120, 230, 140) or Color3.fromRGB(255, 120, 90))
	end
	tocar(res and res.ok and "Compra" or "Erro")
	return res
end


local panels={
 ["IGNIS, o Ferreiro"]=canvas.PainelIgnis,
 ["LOJA DE MOCHILAS"]=canvas.PainelMochilas,
 ["LOJA DE GAMEPASSES"]=canvas.PainelGamepasses,
 ["CONFIGURAÇÕES"]=canvas.PainelConfiguracoes,
}
local renderers={}
local function fecharPaineis()
 for _,p in pairs(panels) do p.Visible=false end
 canvas.PainelInventario.Visible=false
end
local function criarPainel(titulo,corTema,largura,altura,abas)
 local p=assert(panels[titulo],titulo)
 local conteudo=p.Conteudo
 local ativa=abas[1].nome
 local revision=0
 local botoes={}
 local cores={}
 if p:FindFirstChild("Abas") then
  for _,a in abas do
   local b=p.Abas:WaitForChild("Aba"..a.nome)
   botoes[a.nome]=b;cores[b]=b.BackgroundColor3
  end
 end
 local function render()
  if not dados or not p.Visible then return end
  revision+=1
  conteudo:SetAttribute("RenderVersion",revision)
  limparGerados(conteudo)
  for _,a in abas do if a.nome==ativa then a.fn(conteudo) end end
  for nome,b in pairs(botoes) do
   b.BackgroundColor3=nome==ativa and (b:GetAttribute("CorSelecionada") or corTema) or cores[b]
  end
 end
 p.Fechar.Activated:Connect(function() p.Visible=false end)
 for nome,b in pairs(botoes) do
  b.Activated:Connect(function() ativa=nome;render() end)
 end
 local result={frame=p,conteudo=conteudo,render=render,abrir=function()
  fecharPaineis();p.Visible=true;ativa=abas[1].nome;render()
 end}
 table.insert(renderers,render)
 return result
end
local function linha(pai,titulo,sub,textoBotao,corBotao,aoClicar,desativado)
 local f=clone("LinhaLista",pai)
 f.Titulo.Text=titulo
 f.Descricao.Text=sub or ""
 local b=f.Acao
 b.Visible=textoBotao~=nil
 if textoBotao then
  b.Text=textoBotao
  if desativado then
   b.BackgroundColor3=b:GetAttribute("CorDesativado") or b.BackgroundColor3
   b.TextColor3=b:GetAttribute("TextoDesativado") or b.TextColor3
  end
  b.AutoButtonColor=not desativado
  if not desativado and aoClicar then b.Activated:Connect(aoClicar) end
 end
 return f
end
-- ================= PAINEL DO IGNIS: VENDER + PICARETAS =================
local function abaVender(pai)
	local total, itens = 0, 0
	local ordenado = {}
	for id, qtd in pairs(dados.mochila) do
		local def = Config.infoMinerio(id)
		if def then table.insert(ordenado, { def = def, qtd = qtd }) end
	end
	table.sort(ordenado, function(a, b) return a.def.valor > b.def.valor end)
	for _, it in ipairs(ordenado) do
		total = total + it.def.valor * it.qtd
		itens = itens + it.qtd
		local f = linha(pai, it.def.nome .. "  x" .. it.qtd,
			"$ " .. formatar(it.def.valor) .. " cada", nil)
		f:FindFirstChildOfClass("TextLabel").TextColor3 = it.def.cor
	end
	if itens == 0 then
		linha(pai, "Mochila vazia", "Va minerar antes de voltar aqui", nil)
		return
	end
	local final = math.floor(total * (1 + dados.bonusValor))
	linha(pai, "VENDER TUDO", itens .. " itens" ..
		(dados.bonusValor > 0 and string.format("   +%d%% de hats", dados.bonusValor * 100) or ""),
		"$ " .. formatar(final), VERDE, function()
			local r = chamar(R.Vender)
			if r and r.ok then
				avisar("+$ " .. formatar(r.ganho), Color3.fromRGB(255, 215, 90))
				tocar("Moeda")
			end
		end)
end

local function abaPicaretas(pai)
	local _, iAtual = Config.picaretaPorId(dados.picareta)
	for i, p in ipairs(Config.Picaretas) do
		local possui = i <= (iAtual or 1)
		linha(pai, p.nome, "Dano base " .. formatar(p.dano),
			possui and "EM USO" or ("$ " .. formatar(p.custo)),
			possui and VERDE or AZUL,
			function() chamar(R.ComprarPicareta, p.id) end,
			possui or dados.moeda < p.custo)
	end
end

local painelIgnis = criarPainel("IGNIS, o Ferreiro", Color3.fromRGB(255, 150, 55), 620, 440, {
	{ nome = "Vender", fn = abaVender },
	{ nome = "Picaretas", fn = abaPicaretas },
})

-- ================= PAINEL DA LOJA: MOCHILAS =================
local function abaMochilas(pai)
	local _, iAtual = Config.mochilaPorId(dados.mochilaTier)
	for i, m in ipairs(Config.Mochilas) do
		local possui = i <= (iAtual or 1)
		linha(pai, m.nome, "Capacidade " .. formatar(m.capacidade),
			possui and "EM USO" or ("$ " .. formatar(m.custo)),
			possui and VERDE or LARANJA,
			function() chamar(R.ComprarMochila, m.id) end,
			possui or dados.moeda < m.custo)
	end
end

local painelLoja = criarPainel("LOJA DE MOCHILAS", Color3.fromRGB(255, 190, 70), 620, 440, {
	{ nome = "Mochilas", fn = abaMochilas },
})

-- ================= INVENTARIO: GRADE DE ICONES + DETALHE =================
local painelInv
local selecionado = nil          -- { tipo = "hat"|"pet", id = ... }
local abaInv = "Hats"

local function desenharIcone(pai,tipo,id,cor)
 local assetId=tipo=="hat" and Config.HatAssets and Config.HatAssets[id]
 local icon
 if assetId and assetId~=0 then
  icon=clone("ImagemItem",pai)
  icon.Image=("rbxthumb://type=Asset&id=%d&w=150&h=150"):format(assetId)
 else
  local key="Hat"
  if tipo=="pet" then key="Pet"
  elseif id:find("bandana") or id:find("faixa") then key="Bandana"
  elseif id:find("elmo") or id:find("capacete") then key="Elmo"
  elseif id:find("capuz") or id:find("gorro") then key="Capuz"
  elseif id:find("chapeu") then key="Chapeu"
  elseif id:find("coroa") or id:find("halo") or id:find("aura") then key="Coroa"
  elseif id:find("mascara") then key="Mascara" end
  icon=templates.IconesItens[key]:Clone()
  icon.Visible=true;icon:SetAttribute("GeradoPeloControlador",true);icon.Parent=pai
  for _,o in icon:GetDescendants() do
   if o:IsA("Frame") and o:GetAttribute("UsarCorRaridade") then
    o.BackgroundColor3=cor:Lerp(Color3.new(),1-(o:GetAttribute("TomRaridade") or 1))
   end
  end
 end
 icon.Name="Icone"
 return icon
end
painelInv=(function()
 local p=canvas.PainelInventario
 local det=p.Detalhe
 local detStroke=det:FindFirstChildOfClass("UIStroke")
 local vazio=det.Vazio
 local caixaIcone=det.CaixaIcone
 local detNome=det.Nome
 local detRar=det.Raridade
 local stats=det.Stats
 local btnEquipar=det.BotaoEquipar
 local btnFundir=det.BotaoFundir
 local topo=p.Resumo
 local resumoTxt=topo.Texto
 local btnMelhores=topo.Melhores
 local btnLimpar=topo.Limpar
 local grade=p.Grade
 local abas={Hats=p.AbaHats,Pets=p.AbaPets}
 local coresAbas={}
 for _,b in pairs(abas) do coresAbas[b]=b.BackgroundColor3 end
 p.Fechar.Activated:Connect(function() p.Visible=false end)
 local function linhaStat(rotulo,valor,cor)
  local f=clone("LinhaAtributo",stats)
  f.Rotulo.Text=rotulo;f.Valor.Text=tostring(valor)
  if cor then f.Valor.TextColor3=cor end
 end
 local render
	local function mostrarDetalhe()
		local temSel = selecionado ~= nil
		vazio.Visible = not temSel
		caixaIcone.Visible = temSel
		detNome.Visible = temSel
		detRar.Visible = temSel
		stats.Visible = temSel
		btnEquipar.Visible = temSel
		btnFundir.Visible = temSel
		limparGerados(stats)
		limparGerados(caixaIcone)
		if not temSel then return end

		local ehHat = selecionado.tipo == "hat"
		local def = ehHat and Config.hatPorId(selecionado.id) or Config.petPorId(selecionado.id)
		local posse = ehHat and dados.hats[selecionado.id] or dados.pets[selecionado.id]
		if not def or not posse then selecionado = nil; return mostrarDetalhe() end

		local r = Config.Raridades[def.raridade]
		detStroke.Color = r.cor
		desenharIcone(caixaIcone, selecionado.tipo, selecionado.id, r.cor)
		detNome.Text = def.nome
		detNome.TextColor3 = r.cor
		detRar.Text = r.nome .. "   x" .. posse.qtd
		detRar.TextColor3 = r.cor

		linhaStat("Nivel", posse.nivel .. " / " .. (ehHat and Config.HAT_NIVEL_MAX or Config.PET_NIVEL_MAX))
		if ehHat then
			linhaStat("Dano", "+" .. formatar(Config.hatDanoNoNivel(def.dano, posse.nivel)),
				Color3.fromRGB(255, 200, 90))
			if def.extra then
				linhaStat(def.extra, string.format("+%d%%",
					Config.hatExtraNoNivel(def.extraValor, posse.nivel) * 100), Color3.fromRGB(140, 210, 255))
			end
		else
			linhaStat("Velocidade", "+" .. string.format("%.1f",
				Config.petVelocidadeNoNivel(def.velocidade, posse.nivel)), Color3.fromRGB(140, 230, 160))
			if def.extra then
				local v = Config.petExtraNoNivel(def.extraValor, posse.nivel)
				linhaStat(def.extra, def.extra == "dano" and ("+" .. formatar(v))
					or string.format("+%d%%", v * 100), Color3.fromRGB(140, 210, 255))
			end
		end

		local equipados = ehHat and dados.equipados or dados.petsEquipados
		local eq = false
		for _, e in ipairs(equipados) do if e == selecionado.id then eq = true end end

		btnEquipar.Text = eq and "DESEQUIPAR" or "EQUIPAR"
		btnEquipar.BackgroundColor3 = eq and btnEquipar:GetAttribute("CorDesequipar") or btnEquipar:GetAttribute("CorEquipar")

		local nivelMax = ehHat and Config.HAT_NIVEL_MAX or Config.PET_NIVEL_MAX
		if posse.nivel >= nivelMax then
			btnFundir.Text = "NIVEL MAXIMO"
			btnFundir.BackgroundColor3 = btnFundir:GetAttribute("CorIndisponivel")
			btnFundir.AutoButtonColor = false
		else
			local c = ehHat and Config.custoFusao(def.raridade, posse.nivel)
				or Config.custoFusaoPet(def.raridade, posse.nivel)
			local pode = (posse.qtd - 1) >= c.duplicatas and dados.moeda >= c.moeda
			btnFundir.Text = "FUNDIR   $" .. formatar(c.moeda) .. "  +  " .. c.duplicatas .. "x"
			btnFundir.BackgroundColor3 = pode and btnFundir:GetAttribute("CorDisponivel") or btnFundir:GetAttribute("CorIndisponivel")
			btnFundir.AutoButtonColor = pode
		end
	end

	btnEquipar.Activated:Connect(function()
		if not selecionado then return end
		chamar(selecionado.tipo == "hat" and R.EquiparHat or R.EquiparPet, selecionado.id)
	end)
	btnFundir.Activated:Connect(function()
		if not selecionado then return end
		chamar(selecionado.tipo == "hat" and R.FundirHat or R.FundirPet, selecionado.id)
	end)
	btnMelhores.Activated:Connect(function()
		chamar(abaInv == "Hats" and R.EquiparMelhores or R.EquiparMelhoresPets)
	end)
	btnLimpar.Activated:Connect(function()
		chamar(abaInv == "Hats" and R.DesequiparTodos or R.DesequiparPets)
	end)

 local function celula(tipo,id,def,posse,eq)
  local r=Config.Raridades[def.raridade]
  local b=clone("ItemInventario",grade);b.Name=id
  local sel=selecionado and selecionado.id==id and selecionado.tipo==tipo
  b.Borda.Color=r.cor
  b.Borda.Thickness=sel and 4 or (eq and 2.5 or 1.5)
  b.Borda.Transparency=sel and 0 or (eq and .1 or .5)
  b.Quantidade.Text="x"..posse.qtd;b.Quantidade.Visible=posse.qtd>1
  b.Nivel.Text="Nv"..posse.nivel;b.Nivel.Visible=posse.nivel>1
  b.Equipado.Visible=eq==true
  desenharIcone(b.CaixaIcone,tipo,id,r.cor)
  b.Activated:Connect(function() selecionado={tipo=tipo,id=id};render() end)
 end
	render = function()
		if not dados or not p.Visible then return end
		limparGerados(grade)
		for nome, b in pairs(abas) do
			b.BackgroundColor3 = (nome == abaInv) and b:GetAttribute("CorSelecionada") or coresAbas[b]
		end

		local ehHat = abaInv == "Hats"
		local colecao = ehHat and dados.hats or dados.pets
		local equipadosLista = ehHat and dados.equipados or dados.petsEquipados
		local equipados = {}
		for _, id in ipairs(equipadosLista) do equipados[id] = true end

		resumoTxt.Text = ehHat
			and string.format("Hats %d/%d    Equipados %d/%d    Dano +%s",
				dados.totalHats, Config.INVENTARIO_MAX, #dados.equipados, dados.slots, formatar(dados.danoHats))
			or string.format("Pets %d/%d    Equipados %d/%d    Velocidade %.1f",
				dados.totalPets, Config.PET_INVENTARIO_MAX, #dados.petsEquipados, dados.slotsPets, dados.velocidade)

		local lista = {}
		for id, posse in pairs(colecao) do
			local def = ehHat and Config.hatPorId(id) or Config.petPorId(id)
			if def then table.insert(lista, { id = id, def = def, posse = posse, eq = equipados[id] == true }) end
		end
		table.sort(lista, function(a, b)
			if a.eq ~= b.eq then return a.eq end
			local ra, rb = Config.Raridades[a.def.raridade].ordem, Config.Raridades[b.def.raridade].ordem
			if ra ~= rb then return ra > rb end
			return (a.posse.nivel or 1) > (b.posse.nivel or 1)
		end)

		if #lista == 0 then
			local aviso=clone("InventarioVazio",grade)
 aviso.Texto.Text=ehHat and "sem hats" or "sem pets"
		end
		for _, it in ipairs(lista) do
			celula(ehHat and "hat" or "pet", it.id, it.def, it.posse, it.eq)
		end

		mostrarDetalhe()
	end

	for nome, b in pairs(abas) do
		b.Activated:Connect(function()
			abaInv = nome
			selecionado = nil
			render()
		end)
	end

	return { frame = p, render = render,
		abrir = function() fecharPaineis();p.Visible = true; render() end }
end)()

local menu=canvas.MenuLateral
local function botaoHUD(id,rotulo,corBase,corBorda,tipoIcone,ordem,aoClicar)
 local b=menu:WaitForChild("Botao_"..id)
 b.Activated:Connect(aoClicar)
 return b
end
local function alternar(painel)
	if painel.frame.Visible then
		painel.frame.Visible = false
	else
		painelIgnis.frame.Visible = false
		painelLoja.frame.Visible = false
		painelInv.frame.Visible = false
		painel.abrir()
	end
end

local btnInv = botaoHUD("Inventario", "HATS", Color3.fromRGB(58, 128, 214),
	Color3.fromRGB(150, 205, 255), "chapeu", 1, function()
		abaInv = "Hats"
		selecionado = nil
		alternar(painelInv)
	end)

botaoHUD("Pets", "PETS", Color3.fromRGB(150, 90, 210),
	Color3.fromRGB(215, 170, 255), "pet", 4, function()
		abaInv = "Pets"
		selecionado = nil
		alternar(painelInv)
	end)

botaoHUD("Areas", "AREAS", Color3.fromRGB(72, 168, 92),
	Color3.fromRGB(150, 240, 175), "mapa", 5, function()
		if not dados then return end
		local n, total = 0, #Config.Areas
		for _ in pairs(dados.areas) do n += 1 end
		avisar("Areas liberadas: " .. n .. "/" .. total, Color3.fromRGB(150, 240, 175))
	end)

-- tecla B tambem abre
game:GetService("UserInputService").InputBegan:Connect(function(input, digitando)
	if digitando then return end
	if input.KeyCode == Enum.KeyCode.B then
		if painelInv.frame.Visible then
			painelInv.frame.Visible = false
		else
			painelIgnis.frame.Visible = false
			painelLoja.frame.Visible = false
			painelInv.abrir()
		end
	end
end)


R.AbrirGacha.OnClientEvent:Connect(fecharPaineis)
local SLOTS=1
local slotSel=1
local hotbar=canvas.Hotbar
local celulasHB={}
for k=1,SLOTS do
 local b=hotbar:WaitForChild("Slot_"..k)
 celulasHB[k]={botao=b,borda=b.Borda,caixa=b.Caixa}
end
local function conteudoHotbar()
	-- slot unico: a picareta em uso
	local pic = dados and Config.picaretaPorId(dados.picareta)
	local cor = Color3.fromRGB(190, 195, 210)
	if pic and pic.raridade and Config.Raridades[pic.raridade] then
		cor = Config.Raridades[pic.raridade].cor
	end
	return { {
		tipo = "picareta",
		id = dados and dados.picareta or "",
		nome = pic and pic.nome or "Picareta",
		cor = cor,
	} }
end

local function renderHotbar()
 local it=conteudoHotbar()[1]
 local c=celulasHB[1]
 c.caixa.NomePicareta.Text=it.nome
 c.caixa.NomePicareta.TextColor3=it.cor
 c.caixa.Cabeca.BackgroundColor3=it.cor
 c.borda.Color=it.cor
end
local function selecionarSlot(k)
	slotSel = math.clamp(k, 1, SLOTS)
	renderHotbar()
	local itens = conteudoHotbar()
	local it = itens[slotSel]
	if it and it.tipo ~= "picareta" then
		abaInv = (it.tipo == "hat") and "Hats" or "Pets"
		selecionado = { tipo = it.tipo, id = it.id }
		painelIgnis.frame.Visible = false
		painelLoja.frame.Visible = false
		painelInv.abrir()
	elseif it then
		avisar(it.nome, it.cor)
	end
end

for k = 1, SLOTS do
	celulasHB[k].botao.Activated:Connect(function() selecionarSlot(k) end)
end

local TECLAS = { Enum.KeyCode.One, Enum.KeyCode.Two, Enum.KeyCode.Three, Enum.KeyCode.Four,
	Enum.KeyCode.Five, Enum.KeyCode.Six, Enum.KeyCode.Seven, Enum.KeyCode.Eight }
game:GetService("UserInputService").InputBegan:Connect(function(input, digitando)
	if digitando then return end
	for k, tecla in ipairs(TECLAS) do
		if input.KeyCode == tecla then selecionarSlot(k) end
	end
end)

-- ---------- LIGACOES ----------
atualizarUI = function()
	renderHotbar()
	painelIgnis.render()
	painelLoja.render()
	painelInv.render()
end

R.AbrirIgnis.OnClientEvent:Connect(function()
	painelLoja.frame.Visible = false
	painelInv.frame.Visible = false
	painelIgnis.abrir()
end)

R.AbrirLoja.OnClientEvent:Connect(function()
	painelIgnis.frame.Visible = false
	painelInv.frame.Visible = false
	painelLoja.abrir()
end)


local gold=Color3.fromRGB(255,204,85)
local painelPasses = criarPainel("LOJA DE GAMEPASSES", gold, 620, 440, {
 {nome="Gamepasses",fn=function(pai)
  local passes=RS:FindFirstChild("Gamepasses")
  local count=0
  if passes then
   for _,pass in ipairs(passes:GetChildren()) do
    if pass:IsA("IntValue") and pass.Value>0 then
     count+=1
     local row=linha(pai,pass.Name,"Carregando informações...",nil)
 local version=pai:GetAttribute("RenderVersion")
     task.spawn(function()
      local market=game:GetService("MarketplaceService")
      local ok,info=pcall(function() return market:GetProductInfo(pass.Value,Enum.InfoType.GamePass) end)
      if not row.Parent or pai:GetAttribute("RenderVersion")~=version then return end
      row:Destroy()
      if not ok then linha(pai,pass.Name,"Informações indisponíveis. Reabra a loja.",nil) return end
      local ownsOk,owned=pcall(function() return market:UserOwnsGamePassAsync(player.UserId,pass.Value) end)
      if pai:GetAttribute("RenderVersion")~=version then return end
      local available=info.IsForSale and info.PriceInRobux~=nil
      linha(pai,info.Name or pass.Name,info.Description or "",
       owned and ownsOk and "ADQUIRIDO" or (available and ("R$ "..tostring(info.PriceInRobux)) or "INDISPONÍVEL"),
       ROXO,function() market:PromptGamePassPurchase(player,pass.Value) end,
       (ownsOk and owned) or not available)
     end)
    end
   end
  end
  if count==0 then
   linha(pai,"Gamepasses em breve","Nenhum passe disponível no momento.",nil)
  end
 end},
})
botaoHUD("Loja","Loja",gold,gold,"loja",0,function()
 painelIgnis.frame.Visible=false
 painelLoja.frame.Visible=false
 painelInv.frame.Visible=false
 if painelPasses.frame.Visible then painelPasses.frame.Visible=false else painelPasses.abrir() end
end)

botaoHUD("Som",nil,nil,nil,nil,nil,function()
 player:SetAttribute("MusicEnabled",player:GetAttribute("MusicEnabled")==false)
end)
local settings
settings=criarPainel("CONFIGURAÇÕES",gold,520,300,{{nome="Preferências",fn=function(pai)
 linha(pai,"Música","Trilha de cada ilha",player:GetAttribute("MusicEnabled")~=false and "DESLIGAR" or "LIGAR",AZUL,function()
  player:SetAttribute("MusicEnabled",player:GetAttribute("MusicEnabled")==false)
  settings.render()
 end)
 linha(pai,"Efeitos do ambiente","Partículas, pássaros e correnteza",player:GetAttribute("LobbyVFXEnabled")==false and "LIGAR" or "DESLIGAR",ROXO,function()
  player:SetAttribute("LobbyVFXEnabled",player:GetAttribute("LobbyVFXEnabled")==false)
  avisar(player:GetAttribute("LobbyVFXEnabled") and "Efeitos ativados" or "Efeitos reduzidos")
  settings.render()
 end)
end}})
botaoHUD("Config","Config.",Color3.fromRGB(35,38,48),Color3.fromRGB(145,161,195),"config",5,function()
 if settings.frame.Visible then settings.frame.Visible=false else
 painelIgnis.frame.Visible=false painelLoja.frame.Visible=false painelInv.frame.Visible=false
 settings.abrir()
 end
end)

-- Hover parte dos valores editados no Studio.
local sprites={}
for _,b in menu:GetChildren() do
 if b:IsA("TextButton") then
  local face=b.Arte
  local rim=face:FindFirstChildOfClass("UIStroke")
  local hover=face:FindFirstChildOfClass("UIScale")
  local corBase=rim.Color
  local escalaBase=hover.Scale
  b.MouseEnter:Connect(function()
   TS:Create(hover,TweenInfo.new(.15,Enum.EasingStyle.Back),{Scale=escalaBase*1.07}):Play()
   rim.Color=b:GetAttribute("CorHover") or gold
  end)
  b.MouseLeave:Connect(function()
   TS:Create(hover,TweenInfo.new(.15),{Scale=escalaBase}):Play()
   rim.Color=corBase
  end)
  b.MouseButton1Down:Connect(function() hover.Scale=escalaBase*.94 end)
  b.MouseButton1Up:Connect(function() hover.Scale=escalaBase end)
  table.insert(sprites,face)
 end
end
task.spawn(function() pcall(function() game:GetService("ContentProvider"):PreloadAsync(sprites) end) end)
local scale=canvas:WaitForChild("UIScale")
local function resize()
 if tela:GetAttribute("EscalaAutomatica")==false then return end
 local v=tela.AbsoluteSize
 local s=math.min(1,v.X/(tela:GetAttribute("LarguraReferencia") or 1100),v.Y/(tela:GetAttribute("AlturaReferencia") or 700))
 if s<=0 then return end
 scale.Scale=s
 canvas.Size=UDim2.fromOffset(v.X/s,v.Y/s)
end
tela:GetPropertyChangedSignal("AbsoluteSize"):Connect(resize)
resize()
bag.NomeJogador.Text=player.DisplayName
task.spawn(function()
 local ok,url=pcall(function()
  return Players:GetUserThumbnailAsync(player.UserId,Enum.ThumbnailType.HeadShot,Enum.ThumbnailSize.Size150x150)
 end)
 if ok then bag.Retrato.Image=url end
end)
local area=canvas.AreaAtual
local areaPosition=area.Position
local areaVersion=0
local function mostrarArea()
 local id=player:GetAttribute("CurrentAreaId")
 local def=id and Config.areaPorId(id)
 if not def then area.Visible=false;return end
 areaVersion+=1
 local version=areaVersion
 area.Nome.Text=def.nome
 area.Visible=true
 area.Position=areaPosition-UDim2.fromOffset(0,110)
 TS:Create(area,TweenInfo.new(.4,Enum.EasingStyle.Back,Enum.EasingDirection.Out),{Position=areaPosition}):Play()
 task.delay(3.2,function()
  if version~=areaVersion then return end
  TS:Create(area,TweenInfo.new(.45),{Position=areaPosition-UDim2.fromOffset(0,110)}):Play()
  task.wait(.5)
  if version==areaVersion then area.Visible=false;area.Position=areaPosition end
 end)
end
player:GetAttributeChangedSignal("CurrentAreaId"):Connect(mostrarArea)
atualizarUI=function()
 renderHotbar()
 painelInv.render()
 for _,render in renderers do render() end
 if dados then
  local pct=math.floor((dados.bonusValor or 0)*100+.5)
  canvas.Boost.Visible=pct>0
  canvas.Boost.Valor.Text="+"..pct.."%"
 end
end
UIS.InputBegan:Connect(function(input,processed)
 if not processed and input.KeyCode==Enum.KeyCode.Escape then fecharPaineis() end
end)
player:GetAttributeChangedSignal("MusicEnabled"):Connect(settings.render)
player:GetAttributeChangedSignal("LobbyVFXEnabled"):Connect(settings.render)
fecharPaineis()
renderHotbar()
mostrarArea()
if dados then atualizarHUD();atualizarUI() end
