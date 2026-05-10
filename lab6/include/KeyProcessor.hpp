#ifndef KEY_PROCESSOR_HPP
#define KEY_PROCESSOR_HPP

class KeyProcessor {
public:
    enum class Mode {
        Normal,
        Invert,
        Gray,
        Blur,
        Canny,
        Sobel,
        Threshold
    };

    KeyProcessor();

    bool processKey(int key);
    Mode getMode() const;
    const char* getModeName() const;

private:
    Mode currentMode;
};

#endif
