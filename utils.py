class Suggestion:
    def __init__(self, word, prob) -> None:
        self.word = word
        self.prob = prob


def get_suggestions(previous_tokens, n_gram_counts_list, vocabulary, k=1.0, start_with=None):
    """
    Loops over all n-gram counts and returns all suggestions

    Parameters:

        previous_tokens(list): Input Sentence (in the form of tokens)
        n_gram_counts_list(list): List of all n-gram counts
        vocabulary(list): List containing all the words of our vocabulary
        k(float): The value of k-smoothing factor
        start_with(str): First few letters of the next word

    Returns:

        Tuple of suggestions from the auto_complete function
    """

    # See how many models we have
    count = len(n_gram_counts_list)
    print("n = ", count)
    # Empty list for suggestions
    suggestions = []
    # IMP: Earlier "-1"

    # Loop over counts
    for i in range(count-1):
        suggestion = []
        print(i)
        # get n and nplus1 counts
        n_gram_counts = n_gram_counts_list[i]
        nplus1_gram_counts = n_gram_counts_list[i+1]

        # get suggestions
        suggestion = auto_complete(previous_tokens, n_gram_counts,
                                   nplus1_gram_counts, vocabulary,
                                   k=k, start_with=start_with)
        # Append to list
        suggestions += suggestion

    suggestions.sort(key=lambda x: x.prob, reverse=True)
    suggestions = suggestions[:5]
    for item in suggestions:
        print("    ", item.word, " - ", item.prob)
    return map(lambda x: x.word, suggestions)

def auto_complete(previous_tokens, n_gram_counts, nplus1_gram_counts, vocabulary, k=1.0, start_with=None):
    """
    Loops over all words and returns that which has the maximum probability

    Parameters:

        previous_tokens(list): Input Sentence (in the form of tokens)
        n_gram_counts(dict): Dictionary of counts of n-grams
        nplus1_gram_counts(dict): Dictionary of counts of (n+1)-grams
        vocabulary(list): List containing all the words of our vocabulary
        k(float): The value of k-smoothing factor
        start_with(str): First few letters of the next word

    Returns:

        Tuple
         - suggestion(str): The word with max probability
         - max_prob(float): Corresponding probability
    """

    # length of previous words
    n = len(list(n_gram_counts.keys())[0])

    # most recent 'n' words
    previous_n_gram = previous_tokens[-n:]

    # Calculate probabilty for all words
    probabilities = probs(previous_n_gram, n_gram_counts,
                          nplus1_gram_counts, vocabulary, k=k)

    # Intialize the suggestion and max probability
    # suggestion = None
    suggestions = []
    max_prob = 0.008

    # Iterate over all words and probabilites, returning the max.
    # We also add a check if the start_with parameter is provided
    for word, prob in probabilities.items():

        if start_with != None:

            if not word.startswith(start_with):
                continue

        if prob > max_prob:

            suggestion = Suggestion(word, prob)
            suggestions.append(suggestion)

    return suggestions


def probs(previous_n_gram, n_gram_counts, nplus1_gram_counts, vocabulary, k=1.0) -> 'dict':
    """
    This function calculates the Probability for all the words in the vocabulary.

    Parameters:

        previous_n_gram(Sequence): A Sequence containing the previos n-gram
        n_gram_counts(dict): Dictionary of counts of n-grams
        nplus1_gram_counts(dict): Dictionary of counts of (n+1)-grams
        vocabulary(list): List containing all the words of our vocabulary
        k(float): The value of k-smoothing factor

    Returns:

        probabilites(dict): A Dictionary mapping from next words to the probability.

    """

    # Convert to Tuple
    previous_n_gram = tuple(previous_n_gram)

    # Add end and unknown tokens to the vocabulary
    vocabulary = vocabulary + ["<e>", "<unk>"]

    # Calculate the size of the vocabulary
    vocabulary_size = len(vocabulary)

    # Empty dict for probabilites
    probabilities = {}

    # Iterate over words
    for word in vocabulary:

        # Calculate probability
        probability = prob_for_single_word(word, previous_n_gram,
                                           n_gram_counts, nplus1_gram_counts,
                                           vocabulary_size, k=k)
        # Create mapping: word -> probability
        probabilities[word] = probability

    return probabilities


def prob_for_single_word(word, previous_n_gram, n_gram_counts, nplus1_gram_counts, vocabulary_size, k=1.0) -> 'float':
    """
    Calculate Probability for the next word given the prior n-gram.

    Parameters:

        word(str): The next word
        previous_n_gram(Sequence): A Sequence containing the previos n-gram
        n_gram_counts(dict): Dictionary of counts of n-grams
        nplus1_gram_counts(dict): Dictionary of counts of (n+1)-grams
        vocabulary_size(int): The number of words in the vocabulary
        k(float): The value of k-smoothing factor

    Returns:

        prob(float): The probability for the next word.

    """

    # Convert the previous_n_gram into a tuple
    previous_n_gram = tuple(previous_n_gram)

    # Calculating the count, if exists from our freq dictionary otherwise zero
    previous_n_gram_count = n_gram_counts[previous_n_gram] if previous_n_gram in n_gram_counts else 0

    # The Denominator
    denom = previous_n_gram_count + k * vocabulary_size

    # previous n-gram plus the current word as a tuple
    nplus1_gram = previous_n_gram + (word,)

    # Calculating the nplus1 count, if exists from our freq dictionary otherwise zero
    nplus1_gram_count = nplus1_gram_counts[nplus1_gram] if nplus1_gram in nplus1_gram_counts else 0

    # Numerator
    num = nplus1_gram_count + k

    # Final Fraction
    if denom == 0:
        return 0
    prob = num / denom
    return prob
