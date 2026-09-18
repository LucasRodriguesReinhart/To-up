-- Whitelisted device preferences; desktop and landscape phone retain independent sizes.
local U={defaults={desktopScale=.85,mobileScale=.80},min=.65,max=1.15}
function U.value(value)
 if type(value)~="number" or value~=value or math.abs(value)==math.huge then return nil end
 return math.clamp(math.round(value*100)/100,U.min,U.max)
end
function U.sanitize(patch,base)
 local out={}
 for key,default in pairs(U.defaults) do out[key]=U.value(type(patch)=="table" and patch[key]) or U.value(type(base)=="table" and base[key]) or default end
 return out
end
return U
