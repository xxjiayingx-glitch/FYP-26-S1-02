from entity.ProductFeature import ProductFeature

class FeaturesController:

    def get_features(self, offset=0, limit=4):

        feature_entity = ProductFeature()

        features = feature_entity.get_features(offset, limit)

        return features