import Vision
import Quartz
from Foundation import NSURL

def apple_ocr(image_path):
    url = NSURL.fileURLWithPath_(image_path)
    source = Quartz.CGImageSourceCreateWithURL(url, None)
    image = Quartz.CGImageSourceCreateImageAtIndex(source, 0, None)

    request = Vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLanguages_(["it-IT", "en-US"])
    request.setRecognitionLevel_(0) # 0 = Accurate

    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(image, None)
    handler.performRequests_error_([request], None)

    results = request.results()
    if not results:
        return ""
    
    return "\n".join([obs.topCandidates_(1)[0].string() for obs in results])

print(apple_ocr("test_image.jpg"))
