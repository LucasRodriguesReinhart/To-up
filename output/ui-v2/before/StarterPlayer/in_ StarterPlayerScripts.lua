--Model made by @FlayoDev on tiktok
--This only works if your game is public, and only other players can do this. Your feedback gets sent to your dashboard inside roblox create tab.

local Players = game:GetService("Players")
local ProximityPromptService = game:GetService("ProximityPromptService")
local SocialService = game:GetService("SocialService")
local Player = Players.LocalPlayer



ProximityPromptService.PromptShown:Connect(function(ProximityPrompt: ProximityPrompt)
	
	local MailBox = ProximityPrompt.Parent
	
	if MailBox:GetAttribute("Feedback") then --If you make your own prompt, make sure to add a attribute (boolean) named "Feedback" to it. Check the part with proximityprompt in it as example.
		
		ProximityPrompt.Triggered:Connect(function()
			
			SocialService:PromptFeedbackSubmissionAsync()
		end)	
	end
end)
