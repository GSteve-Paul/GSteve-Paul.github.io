---
title: 常用LaTeX表格
date: 2025-10-21
---
## 希腊字母（小写 / 大写）
| 字母 | 符号 | LaTeX 命令 |
|------|------:|-----------|
| alpha / Alpha | α / Α | `\alpha` / `A` |
| beta / Beta | β / Β | `\beta` / `B` |
| gamma / Gamma | γ / Γ | `\gamma` / `\Gamma` |
| delta / Delta | δ / Δ | `\delta` / `\Delta` |
| epsilon / Epsilon | ε / Ε | `\epsilon` 或 `\varepsilon` / `E` |
| zeta / Zeta | ζ / Ζ | `\zeta` / `Z` |
| eta / Eta | η / Η | `\eta` / `H` |
| theta / Theta | θ / Θ | `\theta` 或 `\vartheta` / `\Theta` |
| iota / Iota | ι / Ι | `\iota` / `I` |
| kappa / Kappa | κ / Κ | `\kappa` / `K` |
| lambda / Lambda | λ / Λ | `\lambda` / `\Lambda` |
| mu / Mu | μ / Μ | `\mu` / `M` |
| nu / Nu | ν / Ν | `\nu` / `N` |
| xi / Xi | ξ / Ξ | `\xi` / `\Xi` |
| omicron / Omicron | ο / Ο | `o` / `O` (通常直接写 `o`/`O`) |
| pi / Pi | π / Π | `\pi` / `\Pi` |
| varpi | ϖ | `\varpi` |
| rho / Rho | ρ / Ρ | `\rho` 或 `\varrho` / `P` |
| sigma / Sigma | σ / Σ | `\sigma` 或 `\varsigma` / `\Sigma` |
| tau / Tau | τ / Τ | `\tau` / `T` |
| upsilon / Upsilon | υ / Υ | `\upsilon` / `\Upsilon` |
| phi / Phi | φ / Φ | `\phi` 或 `\varphi` / `\Phi` |
| chi / Chi | χ / Χ | `\chi` / `X` |
| psi / Psi | ψ / Ψ | `\psi` / `\Psi` |
| omega / Omega | ω / Ω | `\omega` / `\Omega` |

---

## 命题逻辑与常用逻辑符号
| 含义 | 符号 | LaTeX 命令 |
|------|------:|-----------|
| 否定 | ¬p | `\neg p` 或 `\lnot p` |
| 合取（且） | p ∧ q | `p \land q` |
| 析取（或） | p ∨ q | `p \lor q` |
| 弱析取（外或） | p ⊕ q | `p \oplus q` |
| 蕴含 | p → q | `p \rightarrow q` 或 `p \to q` |
| 倒蕴含 | p ← q | `p \leftarrow q` |
| 双条件（等价） | p ↔ q | `p \leftrightarrow q` 或 `p \iff q` |
| 真值（恒真/恒假） | ⊤ / ⊥ | `\top` / `\bot` |
| 等价关系符 | ≡ | `\equiv` |
| 同值/约等 | ≈ | `\approx` |
| 推理符号（证明） | ⊢ | `\vdash` |
| 语义满足 | ⊨ | `\models` |
| 不满足/否定模型 | ⊭ | `\not\models` |

---

## 谓词逻辑与量词
| 含义 | 符号 | LaTeX 命令 |
|------|------:|-----------|
| 全称量词 | ∀x P(x) | `\forall x\, P(x)` |
| 存在量词 | ∃x P(x) | `\exists x\, P(x)` |
| 唯一存在 | ∃! x P(x) | `\exists! x\, P(x)` 或 `\exists x\, (P(x)\land \forall y\,(P(y)\rightarrow y=x))` |
| 无存在 | ∄x | `\nexists x` |
| 存在并且仅此 | ⇔（结合） | `\iff` |
| 变量域分隔 | x∈A | `x \in A` |

---

## 集合论与关系
| 含义 | 符号 | LaTeX 命令 |
|------|------:|-----------|
| 属于 / 不属于 | ∈ / ∉ | `\in` / `\notin` |
| 子集 / 真子集 | ⊆ / ⊂ | `\subseteq` / `\subset` |
| 超集 | ⊇ / ⊃ | `\supseteq` / `\supset` |
| 并集 / 交集 | ∪ / ∩ | `\cup` / `\cap` |
| 差集 | A \ B | `A \setminus B` 或 `A - B` |
| 幂集 | P(A) 或 2^A | `\mathcal{P}(A)` 或 `2^{A}` |
| 空集 | ∅ | `\emptyset` 或 `\varnothing` |
| 映射 | f: A → B | `f: A \to B` |
| 等价关系 | ~ | `\sim` |
| 等价类 | [x] | `[x]` |
| Cartesian product | A × B | `A \times B` |

---

## 基本算术与代数符号
| 含义 | 符号 | LaTeX 命令 |
|------|------:|-----------|
| 加 / 减 / 乘 / 除 | + / − / × / ÷ | `+` / `-` / `\times` / `\div` |
| 点乘 / 标量积 | · | `\cdot` |
| 幂 / 指数 | a^b | `a^{b}` |
| 根号 | √ | `\sqrt{x}` 或 `\sqrt[n]{x}` |
| 等于 / 不等于 | = / ≠ | `=` / `\neq` |
| 小于 / 大于 / ≤ / ≥ | < / > / ≤ / ≥ | `<` / `>` / `\le` / `\ge` |
| 四舍五入 / 约等 | ≈ | `\approx` |
| 同余 | ≡ (mod n) | `a \equiv b \pmod n` 或 `\bmod` 系列 |
| 整除 | a | b | `a \mid b`，不整除 `\nmid` |
| 最大公约数 / 最小公倍数 | gcd / lcm | `\gcd(a,b)` / `\operatorname{lcm}(a,b)` |
| 阶乘 | n! | `n!` |
| 二项式系数 | C(n,k) | `\binom{n}{k}` |

---

## 关系符号与比较
| 含义 | 符号 | LaTeX 命令 |
|------|------:|-----------|
| 等价 / 恒等 | ≡ / := | `\equiv` / `:=` （定义用 `\coloneqq`） |
| 相似 / 同构 | ≅ / ≃ | `\cong` / `\simeq` |
| 小于约等 / 大于约等 | ≲ / ≳ | `\lesssim` / `\gtrsim` |
| 顺序关系 | ≺ / ≻ | `\prec` / `\succ` |

---

## 运算符与集合运算（求和、积、极限、积分）
| 含义 | 符号 | LaTeX 命令 |
|------|------:|-----------|
| 求和 | ∑ | `\sum_{i=1}^{n}` |
| 连乘 | ∏ | `\prod_{i=1}^{n}` |
| 极限 | lim | `\lim_{x\to a}` |
| 积分 | ∫ | `\int_{a}^{b}` |
| 多重积分 | ∬ ∭ | `\iint` `\iiint`（需 amsmath 或其他包） |
| 导数 | f'(x) / d/dx | `f'(x)` / `\frac{d}{dx}f(x)` |
| 偏导数 | ∂ | `\frac{\partial f}{\partial x}` 或 `\partial` |
| 拉普拉斯 / ∇ | ∇ / Δ | `\nabla` / `\Delta` |
| 算术极限 / 上确界 | sup / inf | `\sup` / `\inf` |
| 序列收敛 | → | `\to` / 子序列 `\rightharpoonup` 等 |

---

## 括号与定界符
| 含义 | 符号 | LaTeX 命令 |
|------|------:|-----------|
| 小括号 | ( ) | `( ... )` |
| 中括号 | [ ] | `[ ... ]` |
| 大括号（集合） | { } | `\{ ... \}` |
| 尖括号（内积） | ⟨ ⟩ | `\langle ... \rangle` |
| 竖线（条件、绝对值） | \| 或 \mid | `|x|` / `\mid` |
| 双竖线（范数） | ∥ | `\|x\|` |
| 下取整 / 上取整 | ⌊ ⌋ / ⌈ ⌉ | `\lfloor ... \rfloor` / `\lceil ... \rceil` |
| 可伸缩括号 | — | `\left( ... \right)`（任意括号） |
| 单侧空位（配对） | . | `\left. ... \right)` |

---

## 箭头与映射相关
| 含义 | 符号 | LaTeX 命令 |
|------|------:|-----------|
| 右箭头 | → | `\to` / `\rightarrow` |
| 左箭头 | ← | `\leftarrow` |
| 双向箭头 | ↔ | `\leftrightarrow` |
| 长箭头 | ⟶ | `\longrightarrow` |
| 映射定义 | x ↦ f(x) | `x \mapsto f(x)` |
| 同构 / 等价箭头 | ≅（有时用箭头） | `\xrightarrow{\sim}`（需要 `amsmath`） |
| 模 / 同余箭头 | ↦（归约） | `\mapsto` |

---

## 模态 / 其他逻辑扩展（常见）
| 含义 | 符号 | LaTeX 命令 |
|------|------:|-----------|
| 必然（模态逻辑） | □ | `\Box` |
| 可能（模态逻辑） | ◇ | `\Diamond` |
| 贝叶斯 / 条件概率 | P(A|B) | `P(A\mid B)` |
| 归纳 / 推导 | ⇒ | `\Rightarrow` / `\implies` |
| 双向蕴涵 | ⇔ | `\iff` |

---

## 常用装饰与符号（矢量、帽、重音）
| 含义 | 符号 | LaTeX 命令 |
|------|------:|-----------|
| 向量箭头 | \vec{v} | `\vec{v}` |
| 粗体向量 | **v** | `\mathbf{v}` 或 `\boldsymbol{v}` |
| 单帽 | \hat{x} | `\hat{x}` |
| 波浪 | \tilde{x} | `\tilde{x}` |
| 上标 / 下标 | x_i, a^b | `x_{i}` / `a^{b}` |
| 点乘缩写 | · | `\cdot` |
| 导出符号集 | … | `\dots` `\ldots` `\cdots` |
