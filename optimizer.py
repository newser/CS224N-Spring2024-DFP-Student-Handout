from typing import Callable, Iterable, Tuple
import math

import torch
from torch.optim import Optimizer


class AdamW(Optimizer):
    def __init__(
            self,
            params: Iterable[torch.nn.parameter.Parameter],
            lr: float = 1e-3,
            betas: Tuple[float, float] = (0.9, 0.999),
            eps: float = 1e-6,
            weight_decay: float = 0.0,
            correct_bias: bool = True,
    ):
        if lr < 0.0:
            raise ValueError("Invalid learning rate: {} - should be >= 0.0".format(lr))
        if not 0.0 <= betas[0] < 1.0:
            raise ValueError("Invalid beta parameter: {} - should be in [0.0, 1.0[".format(betas[0]))
        if not 0.0 <= betas[1] < 1.0:
            raise ValueError("Invalid beta parameter: {} - should be in [0.0, 1.0[".format(betas[1]))
        if not 0.0 <= eps:
            raise ValueError("Invalid epsilon value: {} - should be >= 0.0".format(eps))
        defaults = dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay, correct_bias=correct_bias)
        super().__init__(params, defaults)

    def step(self, closure: Callable = None):
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            b1, b2 = group['betas']
            eps = group['eps']
            weight_decay = group['weight_decay']

            for p in group["params"]:
                if p.grad is None:
                    continue
                grad = p.grad.data
                if grad.is_sparse:
                    raise RuntimeError("Adam does not support sparse gradients, please consider SparseAdam instead")

                # State should be stored in this dictionary.
                state = self.state[p]

                # Access hyperparameters from the `group` dictionary.
                alpha = group["lr"]

                # Complete the implementation of AdamW here, reading and saving
                # your state in the `state` dictionary above.
                # The hyperparameters can be read from the `group` dictionary
                # (they are lr, betas, eps, weight_decay, as saved in the constructor).
                #
                # To complete this implementation:
                # 1. Update the first and second moments of the gradients.
                # 2. Apply bias correction
                #    (using the "efficient version" given in https://arxiv.org/abs/1412.6980;
                #     also given in the pseudo-code in the project description).
                # 3. Update parameters (p.data).
                # 4. Apply weight decay after the main gradient-based updates.
                # Refer to the default project handout for more details.

                ### TODO
                # raise NotImplementedError

                m = state['m'] if 'm' in state else torch.zeros(*grad.shape, dtype=torch.float32, device=grad.device)
                v = state['v'] if 'v' in state else torch.zeros(*grad.shape, dtype=torch.float32, device=grad.device)
                t = state['t'] if 't' in state else 0
                t += 1

                m = b1 * m + (1 - b1) * grad
                v = b2 * v + (1 - b2) * (grad * grad)

                # mt = m / (1 - b1 ** t)
                # vt = v / (1 - b2 ** t)

                # p_new = p.data - alpha * mt / (torch.sqrt(vt) + group['eps'])
                # p.data = p_new - alpha * group['weight_decay'] * p.data

                alpha_t = alpha * (1 - b2**t)**0.5 / (1 - b1**t)

                p_new = p.data - alpha_t * m / (v**0.5 + eps)
                p.data = p_new - alpha * weight_decay * p.data

                self.state[p]['m'] = m
                self.state[p]['v'] = v
                self.state[p]['t'] = t
                # print(self.state)
                # print(group)

        return loss
