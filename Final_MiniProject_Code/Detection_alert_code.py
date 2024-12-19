from Voice_alert import save_audio,play_audio
save_audio()
def detection_alert(results, names, drowsy_count, phone_use_count):
    clss = results[0].boxes.cls.cpu().tolist()
    conf = results[0].boxes.conf.float().cpu().tolist()

    drowsy_detected = False
    phone_detected = False

    for cls, confidence in zip(clss, conf):
        if names[int(cls)] == "drowsy" and confidence >= 0.5:
            drowsy_detected = True
            drowsy_count += 1

            if drowsy_count == 10:
                play_audio("drowsy")
                drowsy_count = 0

        if names[int(cls)] == "using-phone" and confidence >= 0.3:
            phone_detected = True
            phone_use_count += 1

            if phone_use_count == 10:
                play_audio("using-phone")
                phone_use_count = 0

    if not drowsy_detected:
        drowsy_count = 0
    if not phone_detected:
        phone_use_count = 0

    return drowsy_count, phone_use_count