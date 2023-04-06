#skew-symmetric Matrix

import modern_robotics as mr
import numpy as np

Omega = np.array([1,2,0.5])
skew = mr.VecToso3(Omega)

print(skew)