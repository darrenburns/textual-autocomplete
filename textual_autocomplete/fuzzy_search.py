"""
Fuzzy matcher.

This class is used by the [command palette](/guide/command_palette) to match search terms.

This is the matcher that powers Textual's command palette.

Thanks to Will McGugan for the implementation.
"""

from __future__ import annotations

from operator import itemgetter
from re import IGNORECASE, escape, finditer, search
from typing import Iterable, NamedTuple

from textual.cache import LRUCache


class _Search(NamedTuple):
    """Internal structure to keep track of a recursive search."""

    candidate_offset: int = 0
    query_offset: int = 0
    offsets: tuple[int, ...] = ()

    def branch(self, offset: int) -> tuple[_Search, _Search]:
        """Branch this search when an offset is found.

        Args:
            offset: Offset of a matching letter in the query.

        Returns:
            A pair of search objects.
        """
        _, query_offset, offsets = self
        return (
            _Search(offset + 1, query_offset + 1, offsets + (offset,)),
            _Search(offset + 1, query_offset, offsets),
        )

    @property
    def groups(self) -> int:
        """Number of groups in offsets."""
        groups = 1
        last_offset, *offsets = self.offsets
        for offset in offsets:
            if offset != last_offset + 1:
                groups += 1
            last_offset = offset
        return groups


class FuzzySearch:
    """Performs a fuzzy search.

    Unlike a regex solution, this will finds all possible matches.
    """

    cache: LRUCache[tuple[str, str, bool], tuple[float, tuple[int, ...]]] = LRUCache(
        1024 * 4
    )

    def __init__(self, case_sensitive: bool = False) -> None:
        """Initialize fuzzy search.

        Args:
            case_sensitive: Is the match case sensitive?
        """

        self.case_sensitive = case_sensitive

    def match(self, query: str, candidate: str) -> tuple[float, tuple[int, ...]]:
        """Match against a query.

        Args:
            query: The fuzzy query.
            candidate: A candidate to check,.

        Returns:
            A pair of (score, tuple of offsets). `(0, ())` for no result.
        """
        query_regex = ".*?".join(f"({escape(character)})" for character in query)
        if not search(
            query_regex, candidate, flags=0 if self.case_sensitive else IGNORECASE
        ):
            # Bail out early if there is no possibility of a match
            return (0.0, ())

        cache_key = (query, candidate, self.case_sensitive)
        if cache_key in self.cache:
            return self.cache[cache_key]
        result = max(
            self._match(query, candidate), key=itemgetter(0), default=(0.0, ())
        )
        self.cache[cache_key] = result
        return result

    def _match(
        self, query: str, candidate: str
    ) -> Iterable[tuple[float, tuple[int, ...]]]:
        """Generator to do the matching.

        Args:
            query: Query to match.
            candidate: Candidate to check against.

        Yields:
            Pairs of score and tuple of offsets.
        """
        if not self.case_sensitive:
            query = query.lower()
            candidate = candidate.lower()

        # We need this to give a bonus to first letters.
        first_letters = {match.start() for match in finditer(r"\w+", candidate)}

        def score(search: _Search) -> float:
            """Sore a search.

            Args:
                search: Search object.

            Returns:
                Score.

            """
            # This is a heuristic, and can be tweaked for better results
            # Boost first letter matches
            offset_count = len(search.offsets)
            score: float = offset_count + len(
                first_letters.intersection(search.offsets)
            )
            # Boost to favor less groups
            normalized_groups = (offset_count - (search.groups - 1)) / offset_count
            score *= 1 + (normalized_groups * normalized_groups)
            return score

        stack: list[_Search] = [_Search()]
        push = stack.append
        pop = stack.pop
        query_size = len(query)
        find = candidate.find
        # Limit the number of loops out of an abundance of caution.
        # This should be hard to reach without contrived data.
        remaining_loops = 10_000
        while stack and (remaining_loops := remaining_loops - 1):
            search = pop()
            offset = find(query[search.query_offset], search.candidate_offset)
            if offset != -1:
                if not set(candidate[search.candidate_offset :]).issuperset(
                    query[search.query_offset :]
                ):
                    # Early out if there is not change of a match
                    continue
                advance_branch, branch = search.branch(offset)
                if advance_branch.query_offset == query_size:
                    yield score(advance_branch), advance_branch.offsets
                    push(branch)
                else:
                    push(branch)
                    push(advance_branch)
