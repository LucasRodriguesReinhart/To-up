-- gerado pelo montar da ilha/portoes. Estado de um portao de compra (DB, ShadowGarden, DemonSlayer, OnePiece,
-- OnePunchMan). No SERVIDOR vale para todos; num LocalScript vale so para aquele jogador (quem pagou).
--   require(game.ReplicatedStorage.PortoesCompra).Estado('DB', true)   -- desbloqueia
local CS = game:GetService('CollectionService')
local M = {}
local estado = {}   -- chave -> desbloqueado (sobrevive ao streaming: pecas que chegam depois recebem o estado)
local function aplicar(d)
  local chave = d:GetAttribute('gate'); local desb = estado[chave]
  if desb == nil then return end
  local p = d:GetAttribute('gate_part')
  if p == 'barrier' or p == 'lock' then d.Transparency = desb and 1 or (d:GetAttribute('t0') or 0)
  elseif p == 'openglow' then d.Transparency = desb and 0 or 1
  elseif p == 'lockcol' then d.CanCollide = not desb end
end
function M.Estado(chave, desbloqueado)
  estado[chave] = desbloqueado and true or false
  for _, d in ipairs(CS:GetTagged('PortaoCompra')) do if d:GetAttribute('gate') == chave then aplicar(d) end end
end
function M.Reaplicar() for _, d in ipairs(CS:GetTagged('PortaoCompra')) do aplicar(d) end end
CS:GetInstanceAddedSignal('PortaoCompra'):Connect(aplicar)
function M.Chaves() local s = {} for _, d in ipairs(CS:GetTagged('PortaoCompra')) do s[d:GetAttribute('gate')] = true end return s end
return M
