
import numpy as np
import pandas  as pd

class Fuzzy():
    def __init__(self, inputs, outputs,rule_base_file) -> None:
        """
        Initializes the Fuzzy class with input and output fuzzy variables, builds the fuzzy rule base,
        and modifies the rule table to add median values to the target outputs.

        Parameters:
        inputs : dict
            Dictionary of input fuzzy variables with their respective shapes.
        outputs : dict
            Dictionary of output fuzzy variables with their respective shapes.
        """
        self.inputs = inputs  # Store input fuzzy variables
        self.outputs = outputs  # Store output fuzzy variables

        # Extracts the shape of input variables to understand rule combinations
        self.rule_base = pd.read_csv(rule_base_file)

        # Build the fuzzy rule base (a DataFrame containing all fuzzy rules)
        self.rule_table = self.build_fuzzy_rule_base(inputs, outputs)

        # Modify the target values in the rule table by adding the median to each target
        self.add_median_to_target()

    def add_median_to_target(self):
        """
        Updates the rule table by adding median values to the target outputs.
        For each output key, applies the `get_median` function to its corresponding values.
        """
        for key in self.outputs.keys():
            # Applies the get_median function to each column in the rule table for specified outputs
            self.rule_table[key] = self.rule_table[key].map(self.get_median)

    def get_median(self, array):
        """
        Calculates the median of an array and returns a new array with the first element,
        median, and last element from the original array.

        Parameters:
        array : ndarray
            Array of values for which the median is calculated.

        Returns:
        median : float
            The median value of the array.
        """
        median = np.median(array)  # Calculate the median of the array
        #new_array = np.array([array[0], median, array[-1]])  # Create a new array with start, median, and end values
        return median  # Return the median value (used in add_median_to_target)






    def build_fuzzy_rule_base(self, inputs, outputs):
        """Builds the fuzzy rule base as a DataFrame by generating all possible fuzzy rules
        based on input and output combinations.

        Parameters:
        inputs : dict
            Dictionary containing input variables for fuzzy logic.
        outputs : dict
            Dictionary containing output variables for fuzzy logic.

        Returns:
        rule_table : DataFrame
            A DataFrame where each row represents a fuzzy rule with input and output values.
        """

        rule_tabel = self.rule_base.copy()
        # map the catogres to it values using the input and output values
        for key in inputs.keys():
            rule_tabel[key] = rule_tabel[key].map(inputs[key])

        for key in outputs.keys():

           rule_tabel[key] = rule_tabel[key].map(outputs[key])


        return rule_tabel





    def triangular_mf(self, x, a, b, c):
        """
        Triangular membership function with division by zero handling.

        Parameters:
        x : float or ndarray
            Input value(s) where the membership function is evaluated.
        a : float
            Left endpoint of the triangle (where membership begins to increase).
        b : float
            Peak point of the triangle (where membership is 1).
        c : float
            Right endpoint of the triangle (where membership decreases back to zero).

        Returns:
        float or ndarray
            Membership value(s) corresponding to x.
        """
        # Handle the left side of the triangle
        if b - a == 0:
            left = np.where(x == a, 1.0, 0.0)
        else:
            left = (x - a) / (b - a)

        # Handle the right side of the triangle
        if c - b == 0:
            right = np.where(x == b, 1.0, 0.0)
        else:
            right = (c - x) / (c - b)

        # Combine both sides and ensure non-negative membership values
        return np.maximum(np.minimum(left, right), 0)

    def get_the_firing_rules(self, x):
        """
        Identifies which rules in the rule table are firing (applicable) based on the input x.
        Uses the triangular membership function to evaluate membership values for each rule.

        Parameters:
        x : list or ndarray
            Input values to be evaluated.

        Returns:
        new_rule_table : DataFrame
            Filtered DataFrame containing only the rules with non-zero firing strength.
        """
        # Copy rule_table to avoid modifying the original data
        new_rule_table = self.rule_table.copy()

        # Update the rule table by applying the triangular membership function to each input
        for x_val, key in zip(x, self.inputs.keys()):
            new_rule_table[key] = [self.triangular_mf(x_val, *item) \
                                   for item in new_rule_table[key]]

        # Create a boolean mask for rows where all inputs are greater than 0 (indicating active rules)
        new_rule_table_boolean = (new_rule_table[list(self.inputs.keys())] > 0).all(axis=1)

        # Filter rule table using the boolean mask to retain only the firing rules
        new_rule_table = new_rule_table[new_rule_table_boolean]

        return new_rule_table

    def get_firing_strength(self, rule_table):
        """
        Calculates the firing strength for each rule by finding the minimum membership value
        across all inputs for each rule.

        Parameters:
        rule_table : DataFrame
            DataFrame containing the rules with their respective membership values.

        Returns:
        firing_strength : ndarray
            Array of firing strengths for each rule.
        """
        # Calculate the firing strength as the minimum membership across all inputs in each rule
        firing_strength = rule_table[list(self.inputs.keys())].min(axis=1).values
        return firing_strength.reshape(-1, 1)

    def defuzzification(self, firing_strength, output_values):
        """
        Performs defuzzification using the weighted average method to produce a crisp output.

        Parameters:
        firing_strength : ndarray
            Array of firing strengths for the active rules.
        output_values : ndarray
            Array of output values (e.g., speed and direction) corresponding to each rule.

        Returns:
        float
            Defuzzified output value.
        """
        # Compute the weighted average of output values based on firing strengths
        numerator = np.sum(firing_strength * output_values, axis=0)
        denominator = np.sum(firing_strength)+(1E-10)
        return numerator / denominator  # Return the defuzzified value

    def __call__(self, x):
        """
        Evaluates the fuzzy logic system for a given input x.

        Parameters:
        x : list or ndarray
            Input values to evaluate in the fuzzy system.

        Returns:
        result : ndarray
            Defuzzified output result.
        """
        # Get the rules that are firing based on input x
        new_rule_table = self.get_the_firing_rules(x)
        

        # Calculate the firing strength for each firing rule
        firing_straight = self.get_firing_strength(new_rule_table)

        # Perform defuzzification to get a crisp output
        result = self.defuzzification(firing_straight,
                                      new_rule_table[self.outputs.keys()].to_numpy())
        
        self.new_rule_table = new_rule_table

        return result  # Return the final defuzzified output

