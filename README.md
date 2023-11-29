# LSE DS105A (2023/24) - Week 10: Databases + Data reshaping + Basics of Text Mining

<figure>
    <img src="./figures/DS105L_favicon.png" alt="Image Created with Stable Diffusion"  role="presentation" style="object-fit: cover;width:5em;height:5em;border-radius: 50%;">
    <figcaption>
        <span style="display:inline-block;font-size:0.3em;width:30%;">
        </span>
    </figcaption>

</figure>
<br/>
<br/>

This simple repository contains code and data used in Week 10 of 2023's edition of [DS105A](https://lse-dsi.github.io/DS105/). It includes a demo of a data analysis project involving all the good stuff: scraping with Selenium, creating a database, merging, pivoting and some regular expressions.

<img src="figures/DISCORDIA_favicon.png" style="object-fit: cover;width:8em;height:8em;border-radius: 70%;"/>

This is a sneak peek of the [DISCORDIA project](https://jonjoncardoso.github.io/now.html#project-discordia---uncovering-patterns-of-parliamentary-dissent), a research project led by me with the assistance of research assistants who are former DS105 students!


# 📚 Preparation

If you want to replicate the analysis in this notebook, you will need to:

1. Clone this repository to your computer.
2. Add it to your VS Code workspace.
3. Set up your conda environment:

    ```bash
    conda create -n ds105-w10 python=3.11 ipython
    conda activate ds105-w10
    ```
5. Make sure `pip` is installed inside that environment:

    ```bash
    conda install pip
    ```

6. Now use that pip to install the packages:

    ```bash
    python -m pip install -r requirements.txt
    ```
5. Open the notebook and run the cells!

