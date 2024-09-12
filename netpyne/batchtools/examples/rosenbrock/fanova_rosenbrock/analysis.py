from netpyne.batchtools.analysis import Analyzer

analyzer = Analyzer(params = ['x.0', 'x.1', 'x.2', 'x.3'], metrics = ['fx'])
analyzer.load_file('optuna.csv')
results = analyzer.run_analysis()

