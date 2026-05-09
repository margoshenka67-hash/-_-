#include "KeyProcessor.hpp"

KeyProcessor::KeyProcessor() {
    currentMode = Mode::Normal;
}

bool KeyProcessor::processKey(int key) {
    if (key == -1) {
        return true;
    }

    if (key == 'q' || key == 27) {
        return false;
    }

    switch (key) {
        case '0':
            currentMode = Mode::Normal;
            break;
        case '1':
            currentMode = Mode::Invert;
            break;
        case '2':
            currentMode = Mode::Gray;
            break;
        case '3':
            currentMode = Mode::Blur;
            break;
        case '4':
            currentMode = Mode::Canny;
            break;
        case '5':
            currentMode = Mode::Sobel;
            break;
        case '6':
            currentMode = Mode::Threshold;
            break;
        default:
            break;
    }

    return true;
}

KeyProcessor::Mode KeyProcessor::getMode() const {
    return currentMode;
}

const char* KeyProcessor::getModeName() const {
    switch (currentMode) {
        case Mode::Normal:
            return "Normal";
        case Mode::Invert:
            return "Invert";
        case Mode::Gray:
            return "Grayscale";
        case Mode::Blur:
            return "Gaussian blur";
        case Mode::Canny:
            return "Canny edges";
        case Mode::Sobel:
            return "Sobel";
        case Mode::Threshold:
            return "Threshold";
        default:
            return "Unknown";
    }
}
