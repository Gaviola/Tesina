# Ficha 2.4 — Modelos de lenguaje y adaptación eficiente

Sección del `.tex`: `Chapters/02-Marco-Teorico/04-modelos-lenguaje.tex`.

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

---

## 2.4 Modelos de lenguaje y adaptación eficiente — `sec:marco_llm`

**Mensaje central.** Un LLM es un predictor del siguiente *token* preentrenado a gran escala; se lo
condiciona con texto y se lo adapta con métodos que actualizan pocos parámetros.

**Razón de ser.** El generador de reportes es un LLM con entrada visual; sin este marco no se entienden la
decodificación, el *prompt* ni LoRA. **Extensión: 2,5 páginas.**

**Apertura.** Se elimina «El generador de reportes del pipeline es un modelo de este tipo…» (l. 349–354).
Abre diciendo qué es un modelo de lenguaje y qué necesita saber el lector: cómo se obtiene, cómo genera texto y
cómo se lo adapta.

| Subsección | Se reutiliza | Se recorta / elimina | Nuevo |
|---|---|---|---|
| 2.4.1 Grandes modelos de lenguaje — `sec:marco_llm_grandes` | l. 359–406; `eq:marco_lm`, `eq:marco_temperatura` | **Se elimina** en el último párrafo «se fija y se documenta como un hiperparámetro más del generador» (l. 404–406) o se generaliza | **Contexto y *prompt* (necesario para G3):** un párrafo. El modelo condiciona la salida en el texto que recibe; una instrucción y ejemplos incluidos en el *prompt* orientan el comportamiento sin cambiar los pesos (*in-context learning*, `brown2020language`). Se define *prompt* y se establece que **agregar información al contexto es una forma de condicionar la generación**. Es la base de la variante de RAG de §6 |
| 2.4.2 Ajuste eficiente de parámetros: LoRA — `sec:marco_llm_lora` | l. 411–434; `eq:marco_lora`, `fig:marco_lora` | **Se elimina** l. 436–438 («Uno de los objetivos del trabajo es… y por eso los modelos generativos se adaptan con LoRA…»): decisión propia | **Un párrafo inicial de conexión con 2.1.5:** el ajuste fino completo de 2.1.5 es costoso en memoria; los métodos de ajuste eficiente en parámetros (*parameter-efficient fine-tuning*, PEFT) congelan el modelo y entrenan pocos parámetros nuevos. Se nombra la familia (con `\gls{peft}` si se mantiene la sigla) antes de LoRA |

**Párrafo de transición a 2.5.** Se elimina l. 440–441 tal como está («Un modelo de lenguaje, sin embargo, solo
recibe texto») y se reescribe: hasta acá el modelo procesa texto y el clasificador procesa imágenes; unir los
dos exige una forma de llevar los rasgos de la imagen al espacio de *tokens* del LLM, o de alinear ambas
modalidades en un espacio común. Eso es un modelo visión–lenguaje.
**Citas:** `brown2020language`, `touvron2023llama`, `devlin2019bert`, `ouyang2022training`, `holtzman2020curious`,
`hu2021lora`, `yilmaz2025resourceefficient` (solo si respalda la afirmación sobre costos; se puede pasar al estado del arte).
