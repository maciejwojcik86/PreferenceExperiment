# Experiment Methodology

## 1. Study Design

This experiment utilizes an **LLM-as-a-Judge** framework to evaluate the relative self-preference bias of Large Language Models (LLMs).

### 1.1 Generation
*   **Prompt**: A single, creative writing prompt (e.g., "Write a story about a robot who discovers it loves gardening") is used to generate text samples from all $N$ participating models.
*   **Blindness**: Models generate text independently without knowledge of other models' outputs.

### 1.2 Evaluation
*   **Round-Robin Tournament**: Every model's generation is paired with every other model's generation.
*   **Peer-Review**: Each pair is evaluated by every model in the panel (including the authors of the text).
*   **Judge Instruction**: Judges are asked to select the "better" story based on creativity and structure. To mitigate positional bias, pairs should ideally be swapped, though the current implementation focuses on pairwise distinct combinations.

## 2. Quantitative Metrics

### 2.1 Relative Self-Preference Bias
We define "Bias" as the deviation in a model's win rate when it judges itself versus when it is judged by neutral peers.

$$
Bias(M) = WinRate_{self}(M) - WinRate_{others}(M)
$$

Where:
*   $WinRate_{self}(M)$: The percentage of time Model $M$ votes for itself when presented with its own text versus a competitor.
*   $WinRate_{others}(M)$: The percentage of time other models vote for Model $M$ when comparing it against the same competitors.

A positive score indicates **Self-Preference Bias** (the model prefers itself more than the consensus). A negative score indicates **Self-Deprecation** (the model prefers itself less than the consensus).

### 2.2 Uncertainty Estimation (Agresti-Caffo)
Due to the computationally expensive nature of LLM evaluation, sample sizes ($n$) are often small. Standard Wald Confidence Intervals ($\hat{p} \pm z \sqrt{\hat{p}(1-\hat{p})/n}$) are unreliable for small $n$, especially when rates approach 0% or 100% (where calculated variance becomes 0).

To address this, we employ the **Agresti-Caffo** method (also known as the "Plus Four" confidence interval for difference of proportions). This Bayesian-approximate method effectively adds 1 pseudo-success and 1 pseudo-failure to each sample group.

#### Adjusted Statistics
For each group $i$ (where $i=1$ is Self-Judge, $i=2$ is Other-Judge):

$$
\tilde{n}_i = n_i + 2
$$
$$
\tilde{p}_i = \frac{x_i + 1}{\tilde{n}_i}
$$

#### Margin of Error (95% CI)
The Standard Error (SE) for the difference in adjusted proportions is:

$$
SE_{diff} = \sqrt{ \frac{\tilde{p}_1(1-\tilde{p}_1)}{\tilde{n}_1} + \frac{\tilde{p}_2(1-\tilde{p}_2)}{\tilde{n}_2} }
$$

The 95% Margin of Error is then:

$$
MOE_{95} = 1.96 \times SE_{diff}
$$

We report the Bias Score as $\Delta \tilde{p} \pm MOE_{95}$. This ensures reasonably conservative error bars even with very small sample sizes.

### 2.3 ELO Rating
We calculate standard ELO ratings to determine an overall leaderboard.
*   **Initial Rating**: 1000
*   **K-Factor**: 32

$$
R_A' = R_A + K(S_A - E_A)
$$
$$
E_A = \frac{1}{1 + 10^{(R_B - R_A)/400}}
$$

Where $S_A$ is the actual score (1 for win, 0 for loss) and $E_A$ is the expected score.
