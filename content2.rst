Test
====

Content

#. asd
#. qwe

Another page
============

:math:`2\pi`

Some code
---------

.. code:: matlab

  Settings.Reports.TestCasePlots.LWI_CogErrorEstimation = true;
  Settings.Reports.TestCasePlots.LWI_Spectrogram ...
      = struct('SignalName', 'MF');

Hint:
~~~~~

*It's Matlab*

Final Page
==========

.. plot::

   import matplotlib.pyplot as plt
   import numpy as np
   x = np.random.randn(1000)
   plt.hist( x, 20)
   plt.grid()
   plt.title(r'Normal: $\mu=%.2f, \sigma=%.2f$'%(x.mean(), x.std()))
   plt.show()
