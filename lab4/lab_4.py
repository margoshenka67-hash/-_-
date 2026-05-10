import numpy as np # потрібно для математичних обчислень та роботи з масивами
import matplotlib.pyplot as plt # для візуалізації
from matplotlib.widgets import Slider, Button, CheckButtons # це віджети для інтерактивного керування параметрами
from scipy.signal import butter, filtfilt # для очищення сигналів від шуму


# Початкові параметри (значення, які встановлюються при запуску та після Reset)

INIT_AMPLITUDE = 1.0 # амплітуда
INIT_FREQUENCY = 0.3 # частота
INIT_PHASE = 0.0 # фазовий зсув
INIT_NOISE_MEAN = 0.0 # середнє шуму
INIT_NOISE_COVARIANCE = 0.1 # дисперсія шуму
INIT_CUTOFF = 5.0 # частота зрізу фільтра
INIT_SHOW_NOISE = True # чи показувати шум
INIT_SHOW_FILTERED = True # чи показувати відфільтрований сигнал

# часовий інтервал
T_MIN = 0
T_MAX = 10
N_POINTS = 1000
# крок дискретизації
DT = (T_MAX - T_MIN) / (N_POINTS - 1)
# масив часу
t = np.linspace(T_MIN, T_MAX, N_POINTS)



# Функції

# обчислює чисту гармоніку і гармоніку з шумом
def harmonic_with_noise(t, amplitude, frequency, phase, noise):
    clean_signal = amplitude * np.sin(2 * np.pi * frequency * t + phase)
    noisy_signal = clean_signal + noise
    return clean_signal, noisy_signal

# генерація нормального шуму
def generate_noise(mean, covariance, size):
    std = np.sqrt(max(covariance, 1e-12))
    return np.random.normal(mean, std, size)

# низькочастотний Butterworth фільтр
def lowpass_filter(signal, cutoff_freq, dt, order=4):
    fs = 1.0 / dt # частота дискретизації
    nyquist = fs / 2.0 # частота найквіста

    # обмеження частоти зрізу
    cutoff_freq = max(0.01, min(cutoff_freq, nyquist - 0.01))
    normal_cutoff = cutoff_freq / nyquist

    # коефіцієнти фільтра
    b, a = butter(order, normal_cutoff, btype='low')

    # фільтрація сигналу
    filtered = filtfilt(b, a, signal)
    return filtered

# будує всі сигнали (чистий, з шумом і відфільтрований)
def build_signals():
    clean, noisy = harmonic_with_noise(
        t,
        samp.val,
        sfreq.val,
        sphase.val,
        current_noise if show_noise_state[0] else np.zeros_like(current_noise)
    )

    filtered = lowpass_filter(noisy, scutoff.val, DT)
    return clean, noisy, filtered

# оновлення графіка при зміні параметрів
def update_plot(_=None):
    clean, noisy, filtered = build_signals()

    # оновлюємо дані
    line_clean.set_ydata(clean)
    line_noisy.set_ydata(noisy)

    if show_noise_state[0]:
        line_noisy.set_visible(True)
    else:
        line_noisy.set_visible(False)

    # показ або приховування
    line_filtered.set_ydata(filtered)
    line_filtered.set_visible(show_filtered_state[0])

    fig.canvas.draw_idle() # перемалювати

# викликається при зміні гармоніки (шум не змінюється)
def update_harmonic(_):
    update_plot()

# викликається при зміні параметрів шуму (шум генерується заново)
def update_noise(_):
    global current_noise
    current_noise = generate_noise(snoise_mean.val, snoise_cov.val, len(t))
    update_plot()

# скидання до початкових значень
def reset(event):
    global current_noise

    # повертаємо слайдери
    samp.reset()
    sfreq.reset()
    sphase.reset()
    snoise_mean.reset()
    snoise_cov.reset()
    scutoff.reset()

    # новий шум
    current_noise = generate_noise(
        INIT_NOISE_MEAN,
        INIT_NOISE_COVARIANCE,
        len(t)
    )

    if show_noise_state[0] != INIT_SHOW_NOISE:
        check_noise.set_active(0)

    if show_filtered_state[0] != INIT_SHOW_FILTERED:
        check_filtered.set_active(0)

    update_plot()

# кнопка створити новий шум
def regenerate_noise(event):
    global current_noise
    current_noise = generate_noise(snoise_mean.val, snoise_cov.val, len(t))
    update_plot()

# перемикання показу шуму
def toggle_noise(_):
    show_noise_state[0] = not show_noise_state[0]
    update_plot()

# перемикання показу відфільтрованого сигналу
def toggle_filtered(_):
    show_filtered_state[0] = not show_filtered_state[0]
    update_plot()



# Початковий шум

np.random.seed(42)
current_noise = generate_noise(INIT_NOISE_MEAN, INIT_NOISE_COVARIANCE, len(t))

show_noise_state = [INIT_SHOW_NOISE]
show_filtered_state = [INIT_SHOW_FILTERED]



# Створення вікна

fig, ax = plt.subplots(figsize=(20, 13))

# розташування графіка
plt.subplots_adjust(left=0.08, right=0.70, bottom=0.42)

ax.set_title("Гармоніка з шумом та фільтрацією", fontsize=16)
ax.set_xlabel("t")
ax.set_ylabel("y(t)")
ax.grid(True)

# початкові графіки
initial_clean = INIT_AMPLITUDE * np.sin(2 * np.pi * INIT_FREQUENCY * t + INIT_PHASE)
initial_noisy = initial_clean + current_noise
initial_filtered = lowpass_filter(initial_noisy, INIT_CUTOFF, DT)

line_clean, = ax.plot(t, initial_clean, label='Чиста гармоніка', linewidth=2)
line_noisy, = ax.plot(t, initial_noisy, label='Гармоніка з шумом', linewidth=2, alpha=0.8)
line_filtered, = ax.plot(t, initial_filtered, '--', label='Відфільтрована гармоніка', linewidth=2.5)

ax.legend(loc='upper right')


# Слайдери

ax_amp = plt.axes([0.18, 0.32, 0.50, 0.03])
ax_freq = plt.axes([0.18, 0.27, 0.50, 0.03])
ax_phase = plt.axes([0.18, 0.22, 0.50, 0.03])
ax_noise_mean = plt.axes([0.18, 0.17, 0.50, 0.03])
ax_noise_cov = plt.axes([0.18, 0.12, 0.50, 0.03])
ax_cutoff = plt.axes([0.18, 0.07, 0.50, 0.03])

samp = Slider(ax_amp, 'Amplitude', 0.1, 3.0, valinit=INIT_AMPLITUDE)
sfreq = Slider(ax_freq, 'Frequency', 0.1, 2.0, valinit=INIT_FREQUENCY)
sphase = Slider(ax_phase, 'Phase', 0.0, 2 * np.pi, valinit=INIT_PHASE)
snoise_mean = Slider(ax_noise_mean, 'Noise Mean', -1.0, 1.0, valinit=INIT_NOISE_MEAN)
snoise_cov = Slider(ax_noise_cov, 'Noise Covariance', 0.001, 1.0, valinit=INIT_NOISE_COVARIANCE)
scutoff = Slider(ax_cutoff, 'Cutoff Frequency', 0.1, 20.0, valinit=INIT_CUTOFF)


# Кнопки

ax_reset = plt.axes([0.08, 0.01, 0.12, 0.05])
btn_reset = Button(ax_reset, 'Reset')

ax_new_noise = plt.axes([0.22, 0.01, 0.14, 0.05])
btn_new_noise = Button(ax_new_noise, 'New Noise')


# Чекбокси

ax_check_noise = plt.axes([0.80, 0.22, 0.16, 0.10])
check_noise = CheckButtons(ax_check_noise, ['Show Noise'], [INIT_SHOW_NOISE])

ax_check_filtered = plt.axes([0.80, 0.08, 0.16, 0.10])
check_filtered = CheckButtons(ax_check_filtered, ['Show Filtered'], [INIT_SHOW_FILTERED])


# Інструкція для користувача

instruction_text = (
    "Інструкція:\n"
    "1. Amplitude, Frequency, Phase змінюють параметри гармоніки.\n"
    "2. Noise Mean і Noise Covariance змінюють параметри шуму.\n"
    "3. Після зміни параметрів шуму шум генерується заново.\n"
    "4. Після зміни параметрів гармоніки шум не змінюється.\n"
    "5. Show Noise вмикає/вимикає шум на графіку.\n"
    "6. Show Filtered вмикає/вимикає відфільтрований сигнал.\n"
    "7. Cutoff Frequency змінює частоту зрізу фільтра.\n"
    "8. New Noise генерує нову реалізацію шуму.\n"
    "9. Reset відновлює початкові параметри."
)
fig.text(0.72, 0.82, instruction_text, fontsize=7, va='top')


# Прив'язка подій

samp.on_changed(update_harmonic)
sfreq.on_changed(update_harmonic)
sphase.on_changed(update_harmonic)

snoise_mean.on_changed(update_noise)
snoise_cov.on_changed(update_noise)

scutoff.on_changed(update_plot)

btn_reset.on_clicked(reset)
btn_new_noise.on_clicked(regenerate_noise)

check_noise.on_clicked(toggle_noise)
check_filtered.on_clicked(toggle_filtered)


plt.show()