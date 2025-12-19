import google.generativeai as genai
print("Version:", genai.__version__)
print("Attributes:", dir(genai))
try:
    print("ImageGenerationModel:", genai.ImageGenerationModel)
except AttributeError:
    print("ImageGenerationModel not found")
