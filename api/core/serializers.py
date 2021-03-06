from rest_framework import serializers
from rest_framework.reverse import reverse

from . import models
from .utils import strategy_id


class StrategySerializer(serializers.Serializer):
    """
    Serialize an axelrod strategy object based on
    introspection into its class attributes
    """
    url = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=200)
    description = serializers.SerializerMethodField()
    classifier = serializers.SerializerMethodField()
    params = serializers.SerializerMethodField()

    def get_id(self, strategy):
        return strategy_id(strategy)

    def get_url(self, strategy):
        request = self.context['request']
        return reverse(
            viewname='strategies-detail',
            args=[strategy_id(strategy)],
            request=request)

    def get_description(self, strategy):
        return strategy.__doc__

    def get_classifier(self, strategy):
        classifier = strategy.classifier
        # float('inf') is not valid json
        if classifier['memory_depth'] == float('inf'):
            classifier['memory_depth'] = -1
        return classifier

    def get_params(self, strategy):
        params = strategy.init_params()
        # float('inf') is not valid json
        if 'memory_depth' in params and params['memory_depth'] == float('inf'):
            params['memory_depth'] = -1
        return params


class TournamentDefinitionSerializer(serializers.ModelSerializer):

    @staticmethod
    def validate_player_list(player_list):
        if len(player_list) < 2:
            raise serializers.ValidationError('Ensure this field has at least 2 elements.')
        return player_list

    class Meta:
        model = models.TournamentDefinition
        fields = ('created', 'last_updated', 'turns',
                  'repetitions', 'noise', 'with_morality', 'player_list')


class TournamentSerializer(serializers.ModelSerializer):
    definition = TournamentDefinitionSerializer()

    class Meta:
        model = models.Tournament
        fields = ('id', 'created', 'last_updated', 'status', 'definition', 'results')


class MatchDefinitionSerializer(serializers.ModelSerializer):

    @staticmethod
    def validate_player_list(player_list):
        if len(player_list) != 2:
            raise serializers.ValidationError('Ensure this field has exactly 2 elements.')
        return player_list

    class Meta:
        model = models.MatchDefinition
        fields = ('turns', 'noise', 'player_list')


class MatchSerializer(serializers.ModelSerializer):
    definition = MatchDefinitionSerializer()

    class Meta:
        model = models.Match
        fields = ('id', 'created', 'last_updated', 'status', 'definition', 'results')


class MoranDefinitionSerializer(serializers.ModelSerializer):
    mode = serializers.CharField(min_length=2, max_length=2)

    @staticmethod
    def validate_player_list(player_list):
        if len(player_list) < 2:
            raise serializers.ValidationError('Ensure this field has at least 2 elements.')
        return player_list

    class Meta:
        model = models.MoranDefinition
        fields = ('created', 'last_updated', 'turns', 'noise',
                  'mode', 'player_list')


class MoranSerializer(serializers.ModelSerializer):
    definition = MoranDefinitionSerializer()

    class Meta:
        model = models.Match
        fields = ('id', 'created', 'last_updated', 'status', 'definition', 'results')


class ContestResultSerializer:
    """
    Serialize the result of an axelrod contest into a dictionary by
    iterating over its __dict__ method.
    """

    def __init__(self, result):
        response_object = {}
        for key, value in result.__dict__.items():
            if key not in self.exclude:
                response_object[key] = value

        # we mimic DRF serializer by setting data property instead of returning
        self.data = response_object


class MoranResultsSerializer(ContestResultSerializer):

    handle_locally = [
        'mutation_targets',
        'initial_players',
        'players',
    ]

    exclude = [
        'match_class',
        'deterministic_cache',
    ] + handle_locally

    def __init__(self, result):
        super().__init__(result)
        self.data['mutation_targets'] = self.clean_mutation_targets(result)
        self.data['initial_players'] = [str(s) for s in result.initial_players]
        self.data['players'] = [str(s) for s in result.players]

    @staticmethod
    def clean_mutation_targets(result):
        mutation_targets = {}
        for strategy, target in result.mutation_targets.items():
            mutation_targets[str(strategy)] = [str(s) for s in target]
        return mutation_targets


class MatchResultsSerializer(ContestResultSerializer):

    handle_locally = []

    exclude = [
        '_cache_key',
        '_cache',
        '_players',
        'game',
        'match_attributes',
    ] + handle_locally

    def __init__(self, result):
        super().__init__(result)
        self.data['scores'] = result.scores()
        self.data['final_score'] = result.final_score()
        self.data['final_score_per_turn'] = result.final_score_per_turn()
        self.data['winner'] = str(result.winner())
        self.data['scores'] = result.scores()


class TournamentResultsSerializer(ContestResultSerializer):

    state_distribution_keys = [
    ]

    # keys that have not been implemented
    exclude = [
        'state_distribution',
        'normalised_state_distribution',
        'state_to_action_distribution',
        'normalised_state_to_action_distribution',
        'game',
        'progress_bar'
    ]
